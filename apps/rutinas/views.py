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
def crear_rutina(request):
    import json

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        objetivo = request.POST.get("objetivo")
        imc_min = request.POST.get("imc_min")
        imc_max = request.POST.get("imc_max")
        contenido_json = request.POST.get("contenido")  # viene armado desde JS

        rutina = RutinaBase.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            objetivo=objetivo,
            imc_min=imc_min,
            imc_max=imc_max,
            contenido=contenido_json
        )

        messages.success(request, "Rutina creada correctamente.")
        return redirect('lista_rutinas')

    # JSON vacío para el editor  
    contenido_vacio = {}

    return render(request, 'rutinas/crear_rutina.html', {
        'rutina': None,
        'RUTINA_INICIAL': json.dumps(contenido_vacio),
        'ejercicios': []
    })



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

    import json

    # Convertir contenido JSON a diccionario Python
    try:
        contenido = json.loads(rutina.contenido)
    except:
        contenido = {}

    # ---- APLANAR para mostrar en tabla ----
    ejercicios_lista = []
    for semana, dias in contenido.items():
        numero_semana = int(semana.replace("semana", ""))

        for dia, ejercicios in dias.items():
            numero_dia = int(dia.replace("dia", ""))

            for ej in ejercicios:
                ejercicios_lista.append({
                    "semana": numero_semana,
                    "dia": numero_dia,
                    "ejercicio": ej["ejercicio"],
                    "series": ej["series"],
                    "reps": ej["reps"],
                    "descanso": ej["descanso"]
                })

    # ---- POST (GUARDAR) ----
    if request.method == 'POST':
        rutina.titulo = request.POST.get('titulo')
        rutina.descripcion = request.POST.get('descripcion')
        rutina.objetivo = request.POST.get('objetivo')
        rutina.imc_min = request.POST.get('imc_min')
        rutina.imc_max = request.POST.get('imc_max')

        # Recuperar todos los ejercicios del formulario
        semanas = request.POST.getlist('semana[]')
        dias = request.POST.getlist('dia[]')
        ejercicios = request.POST.getlist('ejercicio[]')
        series = request.POST.getlist('series[]')
        reps = request.POST.getlist('reps[]')
        descansos = request.POST.getlist('descanso[]')

        nuevo_json = {}

        for i in range(len(ejercicios)):
            semana_key = f"semana{semanas[i]}"
            dia_key = f"dia{dias[i]}"

            if semana_key not in nuevo_json:
                nuevo_json[semana_key] = {}

            if dia_key not in nuevo_json[semana_key]:
                nuevo_json[semana_key][dia_key] = []

            nuevo_json[semana_key][dia_key].append({
                "ejercicio": ejercicios[i],
                "series": int(series[i]),
                "reps": reps[i],
                "descanso": descansos[i]
            })

        rutina.contenido = json.dumps(nuevo_json, indent=4, ensure_ascii=False)
        rutina.save()

        messages.success(request, "Rutina modificada correctamente.")
        return redirect('lista_rutinas')

    return render(request, 'rutinas/editar_rutina.html', {
        'rutina': rutina,
        'ejercicios': ejercicios_lista
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
