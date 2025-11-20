from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.socios.models import Socio
from apps.rutinas.models import Rutina, RutinaBase
from apps.core.utils import formatear_rut
from django.utils import timezone
from django import forms


# =======================================================
# 🧩 PERMISOS
# =======================================================
def es_profesor(user):
    """Permite acceso solo a usuarios con rol 'profesor'."""
    return user.is_authenticated and user.rol == 'profesor'


# =======================================================
# 👨‍🏫 MIS ALUMNOS (panel del profesor)
# =======================================================
@login_required
@user_passes_test(es_profesor)
def mis_alumnos(request):
    """Muestra todos los socios asignados al profesor."""
    alumnos = Socio.objects.filter(profesor_asignado=request.user).order_by('nombre')
    for alumno in alumnos:
        alumno.rut_formateado = formatear_rut(alumno.rut)
        alumno.imc_valor = alumno.imc or "N/D"
    return render(request, 'rutinas/mis_alumnos.html', {'alumnos': alumnos})


# =======================================================
# ⚙️ GENERAR RUTINA AUTOMÁTICA
# =======================================================
@login_required
@user_passes_test(es_profesor)
def generar_rutina_automatica(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id, profesor_asignado=request.user)

    if not socio.peso or not socio.altura:
        messages.error(request, "⚠️ No hay información de peso o altura para generar rutina automática.")
        return redirect('mis_alumnos')

    if not socio.objetivo:
        messages.error(request, "⚠️ No se ha definido el objetivo del socio.")
        return redirect('mis_alumnos')

    imc = socio.imc

    plantilla = RutinaBase.objects.filter(
        imc_min__lte=imc,
        imc_max__gte=imc,
        objetivo=socio.objetivo
    ).first()

    if not plantilla:
        messages.warning(request, f"⚠️ No hay una rutina predefinida para IMC {imc} y objetivo '{socio.get_objetivo_display()}'.")
        return redirect('mis_alumnos')

    rutina = Rutina.objects.create(
        profesor=request.user,
        socio=socio,
        titulo=f"{plantilla.titulo} - {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}",
        descripcion=plantilla.descripcion,
        contenido=plantilla.contenido,
        imc_referencia=imc,
        estado='activa'
    )

    rutina.generar_pdf()

    messages.success(request, f"✅ Rutina generada automáticamente para {socio.nombre} ({socio.get_objetivo_display()}).")
    return redirect('mis_alumnos')


# =======================================================
# 📋 CRUD DE RUTINAS (profesor)
# =======================================================




class RutinaBaseForm(forms.ModelForm):
    class Meta:
        model = RutinaBase
        fields = ['titulo', 'descripcion', 'objetivo', 'imc_min', 'imc_max', 'contenido']




@login_required
@user_passes_test(es_profesor)
def lista_rutinas(request):
    """Lista todas las rutinas base disponibles (plantillas)"""
    rutinas = RutinaBase.objects.all().order_by('objetivo', 'imc_min')
    return render(request, 'rutinas/lista_rutinas.html', {'rutinas': rutinas})


@login_required
@user_passes_test(es_profesor)
def editar_rutina(request, rutina_id):
    rutina = get_object_or_404(RutinaBase, id=rutina_id)

    if request.method == 'POST':
        form = RutinaBaseForm(request.POST, instance=rutina)
        if form.is_valid():
            form.save()
            messages.success(request, "Rutina modificada correctamente.")
            return redirect('lista_rutinas')
    else:
        form = RutinaBaseForm(instance=rutina)

    return render(request, 'rutinas/editar_rutina.html', {
        'form': form,
        'rutina': rutina,
    })

    return render(request, 'rutinas/editar_rutina.html', {'rutina': rutina})




@login_required
@user_passes_test(es_profesor)
def eliminar_rutina(request, rutina_id):
    rutina = get_object_or_404(RutinaBase, id=rutina_id)
    titulo = rutina.titulo

    rutina.delete()

    messages.success(request, f"🗑️ La rutina «{titulo}» fue eliminada correctamente.")
    return redirect('lista_rutinas')



# =======================================================
# ➕ PLACEHOLDERS PARA EVITAR ERRORES DE NAVEGACIÓN
# =======================================================
@login_required
@user_passes_test(es_profesor)
def crear_rutina(request):
    messages.info(request, "Funcionalidad de creación manual de rutinas aún no implementada.")
    return redirect('lista_rutinas')


@login_required
@user_passes_test(es_profesor)
def ver_rutina(request, rutina_id):
    messages.info(request, f"Vista de detalle de rutina {rutina_id} aún en desarrollo.")
    return redirect('lista_rutinas')



# =======================================================
# 🧍‍♂️ RUTINAS DEL SOCIO (HISTORIAL)
# =======================================================
from apps.core.decorators import es_socio

@login_required
@user_passes_test(es_socio)
def mis_rutinas_socio(request):
    """Muestra todas las rutinas asignadas al socio."""
    socio = get_object_or_404(Socio, rut=request.user.rut)
    rutinas = Rutina.objects.filter(socio=socio).order_by('-fecha_asignacion')

    context = {
        'socio': socio,
        'rutinas': rutinas,
    }
    return render(request, 'rutinas/mis_rutinas_socio.html', context)
