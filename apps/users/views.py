# apps/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Usuario
from django.contrib import messages
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

# ===============================
# 🧰 CONTROL DE ROLES
# ===============================
def es_superadmin(user):
    """Solo usuarios con rol superadmin pueden acceder"""
    return user.is_authenticated and user.rol == 'superadmin'

def es_admin(user):
    """Solo usuarios con rol admin pueden acceder"""
    return user.is_authenticated and user.rol == 'admin'

def es_profesor(user):
    """Solo usuarios con rol profesor pueden acceder"""
    return user.is_authenticated and user.rol == 'profesor'

def es_socio(user):
    """Solo usuarios con rol socio pueden acceder"""
    return user.is_authenticated and user.rol == 'socio'

# ===============================
# 🧭 DASHBOARDS POR ROL
# ===============================


@login_required
@user_passes_test(es_superadmin)
def dashboard_superadmin(request):
    return render(request, 'dashboards/dashboard_superadmin.html')

@login_required
@user_passes_test(es_admin)
def dashboard_admin(request):
    return render(request, 'dashboards/dashboard_admin.html')

@login_required
@user_passes_test(es_profesor)
def dashboard_profesor(request):
    return render(request, 'dashboards/dashboard_profesor.html')

@login_required
@user_passes_test(es_socio)
def dashboard_socio(request):
    return render(request, 'dashboards/dashboard_socio.html')
                        
# ===============================
# 🧩 AUTENTICACIÓN
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



def formatear_rut(rut):
    """Formatea un RUT chileno sin puntos ni guion -> con puntos y guion."""
    try:
        rut = str(rut)
        cuerpo, dv = rut[:-1], rut[-1]
        cuerpo_con_puntos = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_con_puntos}-{dv.upper()}"
    except Exception:
        return rut 




# ===============================
# 👥 CRUD DE USUARIOS
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
        password = rut

        # ⚠️ Verificar duplicados
        if Usuario.objects.filter(rut=rut).exists():
            return redirect('/usuarios/?error=exists')

        # ✅ Crear usuario
        Usuario.objects.create_user(
            rut=rut,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            rol=rol,
            password=password
        )
        return redirect('/usuarios/?success=created')

    return render(request, 'users/form_usuario.html', {'titulo': 'Crear Usuario'})


@login_required
@user_passes_test(es_superadmin)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('nombre')
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

        # ⚠️ Validar duplicado de RUT si cambió
        if nuevo_rut != usuario.rut:
            if Usuario.objects.filter(rut=nuevo_rut).exclude(id=usuario.id).exists():
                return redirect('/usuarios/?error=exists')
            usuario.rut = nuevo_rut

        usuario.save()
        return redirect('/usuarios/?success=updated')

    return render(request, 'users/form_usuario.html', {
        'usuario': usuario,
        'titulo': 'Editar Usuario'
    })


@login_required
@user_passes_test(es_superadmin)
def eliminar_usuario(request, user_id):
    """Elimina un usuario del sistema"""
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    return redirect('/usuarios/?success=deleted')


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

                Usuario.objects.create(
                    rut=rut,
                    nombre=row['nombre'],
                    apellido=row['apellido'],
                    
                    correo=row['correo'],
                    rol=row['rol'],
                    password=make_password(str(row['rut'])),
                    is_active=True,
                )
                creados += 1

            messages.success(request, f"✅ {creados} usuarios creados correctamente.")

        except Exception as e:
            messages.error(request, f"❌ Error al procesar el archivo: {e}")

        return redirect('lista_usuarios')

    return redirect('lista_usuarios')


# --- PERFIL DE USUARIO / CONFIGURACIÓN ---


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
