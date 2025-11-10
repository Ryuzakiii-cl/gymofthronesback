# apps/users/views.py
from apps.core.utils import formatear_rut
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Usuario
from apps.core.decorators import es_superadmin, es_admin, es_profesor, es_socio
import pandas as pd
import os

from apps.socios.models import Socio
from apps.rutinas.models import Rutina
from apps.talleres.models import Taller

# ===============================
# DASHBOARDS POR ROL
# ===============================

@login_required
@user_passes_test(es_superadmin)
def dashboard_superadmin(request):
    """Panel principal del Superadmin: vista general del sistema."""
    from apps.socios.models import Socio
    from apps.users.models import Usuario
    from apps.rutinas.models import Rutina
    from apps.planes.models import Plan, SocioPlan

    # 👥 Totales por rol
    total_admins = Usuario.objects.filter(rol='admin').count()
    total_profesores = Usuario.objects.filter(rol='profesor').count()
    total_socios = Usuario.objects.filter(rol='socio').count()

    # 💪 Socios activos/inactivos
    socios_activos = Socio.objects.filter(estado=True).count()
    socios_inactivos = Socio.objects.filter(estado=False).count()

    # 🧾 Rutinas y planes
    rutinas_activas = Rutina.objects.filter(estado='activa').count()
    rutinas_totales = Rutina.objects.count()

    planes_vigentes = SocioPlan.objects.filter(estado=True).count()
    planes_vencidos = SocioPlan.objects.filter(estado=False).count()

    # 🕒 Últimos registros
    ultimos_socios = Socio.objects.order_by('-fec_registro')[:5]
    ultimas_rutinas = Rutina.objects.order_by('-fecha_asignacion')[:5]

    context = {
        'total_admins': total_admins,
        'total_profesores': total_profesores,
        'total_socios': total_socios,
        'socios_activos': socios_activos,
        'socios_inactivos': socios_inactivos,
        'rutinas_activas': rutinas_activas,
        'rutinas_totales': rutinas_totales,
        'planes_vigentes': planes_vigentes,
        'planes_vencidos': planes_vencidos,
        'ultimos_socios': ultimos_socios,
        'ultimas_rutinas': ultimas_rutinas,
    }

    return render(request, 'dashboards/dashboard_superadmin.html', context)


@login_required
@user_passes_test(es_admin)
def dashboard_admin(request):
    """Panel principal del Admin: vista general del sistema."""
    from apps.socios.models import Socio
    from apps.users.models import Usuario
    from apps.rutinas.models import Rutina
    from apps.planes.models import Plan, SocioPlan

    # 👥 Totales por rol
    total_admins = Usuario.objects.filter(rol='admin').count()
    total_profesores = Usuario.objects.filter(rol='profesor').count()
    total_socios = Usuario.objects.filter(rol='socio').count()

    # 💪 Socios activos/inactivos
    socios_activos = Socio.objects.filter(estado=True).count()
    socios_inactivos = Socio.objects.filter(estado=False).count()

    # 🧾 Rutinas y planes
    rutinas_activas = Rutina.objects.filter(estado='activa').count()
    rutinas_totales = Rutina.objects.count()

    planes_vigentes = SocioPlan.objects.filter(estado=True).count()
    planes_vencidos = SocioPlan.objects.filter(estado=False).count()

    # 🕒 Últimos registros
    ultimos_socios = Socio.objects.order_by('-fec_registro')[:5]
    ultimas_rutinas = Rutina.objects.order_by('-fecha_asignacion')[:5]

    context = {
        'total_admins': total_admins,
        'total_profesores': total_profesores,
        'total_socios': total_socios,
        'socios_activos': socios_activos,
        'socios_inactivos': socios_inactivos,
        'rutinas_activas': rutinas_activas,
        'rutinas_totales': rutinas_totales,
        'planes_vigentes': planes_vigentes,
        'planes_vencidos': planes_vencidos,
        'ultimos_socios': ultimos_socios,
        'ultimas_rutinas': ultimas_rutinas,
    }

    return render(request, 'dashboards/dashboard_admin.html', context)




@login_required
@user_passes_test(es_profesor)
def dashboard_profesor(request):
    """Panel principal del profesor con métricas."""
    profesor = request.user

    # 🔹 Contar alumnos asignados
    total_alumnos = Socio.objects.filter(profesor_asignado=profesor).count()

    # 🔹 Contar rutinas activas
    rutinas_activas = Rutina.objects.filter(profesor=profesor, estado='activa').count()

    # 🔹 Contar talleres si existe el modelo
    try:
        talleres_asignados = Taller.objects.filter(profesor=profesor).count()
    except Exception:
        talleres_asignados = 0

    context = {
        'total_alumnos': total_alumnos,
        'rutinas_activas': rutinas_activas,
        'talleres_asignados': talleres_asignados,
    }

    return render(request, 'dashboards/dashboard_profesor.html', context)


@login_required
@user_passes_test(es_socio)
def dashboard_socio(request):
    """Panel principal del socio: muestra su información, plan, profesor y estado físico."""
    socio = Socio.objects.filter(rut=request.user.rut).select_related('profesor_asignado').first()

    if not socio:
        messages.warning(request, "No se encontró información de socio asociada a tu cuenta.")
        return render(request, 'dashboards/dashboard_socio.html', {'socio': None})

    context = {
        'socio': socio,
    }
    return render(request, 'dashboards/dashboard_socio.html', context)



# ===============================
# AUTENTICACIÓN
# ===============================
def login_view(request):
    """Pantalla de inicio de sesión"""
    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, rut=rut, password=password)
        if user is not None:
            login(request, user)
            # Redirección según rol
            if user.rol == 'superadmin':
                return redirect('dashboard_superadmin')
            elif user.rol == 'admin':
                return redirect('dashboard_admin')
            elif user.rol == 'profesor':
                return redirect('dashboard_profesor')
            elif user.rol == 'socio':
                return redirect('dashboard_socio')
            else:
                return redirect('/users/login/?error=sinrol')
        else:
            return redirect('/users/login/?error=invalid')

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """Cierra sesión y redirige al login"""
    logout(request)
    return redirect('/users/login/?success=logout')


# ===============================
# CRUD DE USUARIOS
# ===============================

@login_required
@user_passes_test(es_superadmin)
def crear_usuario(request):
    """Crea un nuevo usuario"""
    if request.method == 'POST':
        rut = request.POST['rut']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        rol = request.POST['rol']
        especialidad = request.POST.get('especialidad')
        password = rut

        # ⚠️ Verificar duplicados
        if Usuario.objects.filter(rut=rut).exists():
            return redirect('/usuarios/?error=exists')

        # ✅ Crear usuario base
        user = Usuario.objects.create_user(
            rut=rut,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            rol=rol,
            password=password
        )

        # 🔹 Solo guardar especialidad si es profesor, si no => 'no_aplica'
        if rol == 'Profesor':
            user.especialidad = especialidad or None
        else:
            user.especialidad = 'no_aplica'
        user.save()
        return redirect(f"{reverse('lista_usuarios')}?success=created")

    especialidades = Usuario.ESPECIALIDAD_CHOICES
    return render(request, 'users/form_usuario.html', {
        'titulo': 'Crear Usuario',
        'especialidades': especialidades
    })


@login_required
@user_passes_test(es_superadmin)
def lista_usuarios(request):
    usuarios = Usuario.objects.exclude(rol__iexact='socio').order_by('nombre')
    for u in usuarios:
        u.rut_formateado = formatear_rut(u.rut)
    return render(request, 'users/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(es_superadmin)
def editar_usuario(request, user_id):
    """Edita un usuario existente"""
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        nuevo_rut = request.POST['rut'].strip()
        usuario.nombre = request.POST['nombre']
        usuario.apellido = request.POST['apellido']
        usuario.correo = request.POST['correo']
        usuario.rol = request.POST['rol']
        usuario.is_active = 'is_active' in request.POST
        especialidad = request.POST.get('especialidad') 

        if usuario.rol == 'profesor':
            usuario.especialidad = especialidad or None
        else:
            usuario.especialidad = 'no_aplica'

        if nuevo_rut != usuario.rut:
            if Usuario.objects.filter(rut=nuevo_rut).exclude(id=usuario.id).exists():
                return redirect('/usuarios/?error=exists')
            usuario.rut = nuevo_rut

        usuario.save()
        return redirect(f"{reverse('lista_usuarios')}?success=updated")

    especialidades = Usuario.ESPECIALIDAD_CHOICES
    return render(request, 'users/form_usuario.html', {
        'usuario': usuario,
        'titulo': 'Editar Usuario',
        'especialidades': especialidades
    })


@login_required
@user_passes_test(es_superadmin)
def eliminar_usuario(request, user_id):
    """Elimina un usuario del sistema"""
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    return redirect(f"{reverse('lista_usuarios')}?success=deleted")


# ===============================
# ERROR 404
# ===============================
def error_404(request, exception=None):
    """Página personalizada para errores 404"""
    return render(request, 'core/404.html', status=404)


# ===============================
# CARGA MASIVA DE DATOS
# ===============================
@login_required
@user_passes_test(es_superadmin)
def carga_usuarios(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        extension = os.path.splitext(archivo.name)[1].lower()
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        ruta = fs.save(archivo.name, archivo)
        archivo_path = fs.path(ruta)

        try:
            if extension == '.csv':
                df = pd.read_csv(archivo_path)
            else:
                df = pd.read_excel(archivo_path)

            for col in ['rut', 'nombre', 'apellido', 'correo', 'rol']:
                if col not in df.columns:
                    messages.error(request, f"Falta la columna '{col}' en el archivo.")
                    return redirect('lista_usuarios')

            creados = 0
            for _, row in df.iterrows():
                rut = str(row['rut']).replace('.', '').upper()

                # Evitar duplicados
                if Usuario.objects.filter(rut=rut).exists():
                    continue

                rol = row['rol']
                especialidad = (
                    row['especialidad'] if 'especialidad' in df.columns and rol == 'profesor'
                    else 'no_aplica'
                )

                Usuario.objects.create(
                    rut=rut,
                    nombre=row['nombre'],
                    apellido=row['apellido'],
                    correo=row['correo'],
                    rol=rol,
                    especialidad=especialidad,
                    password=make_password(str(row['rut'])),
                    is_active=True,
                )
                creados += 1

            messages.success(request, f"✅ {creados} usuarios creados correctamente.")

        except Exception as e:
            messages.error(request, f"❌ Error al procesar el archivo: {e}")

        return redirect('lista_usuarios')

    return redirect('lista_usuarios')


# ===============================
# CONFIGURACIÓN DE CUENTA
# ===============================
@login_required
def perfil_usuario(request):
    """Vista principal del panel de cuenta (perfil del usuario)"""
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action')

        # 🧩 Cambiar contraseña
        if action == 'password':
            actual = request.POST.get('password_actual')
            nueva = request.POST.get('password_nueva')
            confirmar = request.POST.get('password_confirmar')

            if not check_password(actual, user.password):
                messages.error(request, "La contraseña actual no es correcta.")
            elif nueva != confirmar:
                messages.error(request, "Las contraseñas nuevas no coinciden.")
            else:
                user.set_password(nueva)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")

        elif action == 'datos':
            user.nombre = request.POST.get('nombre')
            user.apellido = request.POST.get('apellido')
            user.correo = request.POST.get('correo')
            user.save()
            messages.success(request, "Datos personales actualizados correctamente.")

        # ❌ Eliminar cuenta (solo socio y profesor)
        elif action == 'eliminar':
            if user.rol in ['socio', 'profesor']:
                from apps.socios.models import Socio
                Socio.objects.filter(rut=user.rut).delete()
                user.delete()
                messages.success(request, "Tu cuenta ha sido eliminada.")
                return redirect('login')
            else:
                messages.warning(request, "No puedes eliminar esta cuenta.")

    return render(request, 'users/perfil.html', {'user': user})
