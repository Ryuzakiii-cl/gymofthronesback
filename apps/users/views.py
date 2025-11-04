# apps/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Usuario
from django.contrib import messages
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from django.contrib.auth.hashers import make_password


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
                return redirect('/usuarios/login/?error=sinrol')
        else:
            return redirect('/usuarios/login/?error=invalid')

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
        return rut  # si viene vacío o mal formado, se deja igual



# ===============================
# 🧭 DASHBOARDS POR ROL
# ===============================
@login_required
def dashboard_superadmin(request):
    return render(request, 'dashboards/dashboard_superadmin.html')

@login_required
def dashboard_admin(request):
    return render(request, 'dashboards/dashboard_admin.html')

@login_required
def dashboard_profesor(request):
    return render(request, 'dashboards/dashboard_profesor.html')

@login_required
def dashboard_socio(request):
    return render(request, 'dashboards/dashboard_socio.html')


# ===============================
# 🧰 CONTROL DE ROLES
# ===============================
def es_superadmin(user):
    """Solo usuarios con rol superadmin pueden acceder"""
    return user.is_authenticated and user.rol == 'superadmin'


# ===============================
# 👥 CRUD DE USUARIOS
# ===============================
@login_required
@user_passes_test(es_superadmin)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('nombre')
    for u in usuarios:
        u.rut_formateado = formatear_rut(u.rut)
    return render(request, 'users/lista_usuarios.html', {'usuarios': usuarios})




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
        password = request.POST['password']

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
# 🚫 ERROR 404 PERSONALIZADO
# ===============================
def error_404(request, exception=None):
    """Página personalizada para errores 404"""
    return render(request, 'core/404.html', status=404)





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
            # Leer Excel o CSV
            if extension == '.csv':
                df = pd.read_csv(archivo_path)
            else:
                df = pd.read_excel(archivo_path)

            columnas = ['rut', 'nombre', 'apellido', 'correo', 'rol', 'contraseña']
            for col in ['rut', 'nombre', 'apellido', 'correo', 'rol', 'contraseña']:
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
                    password=make_password(str(row['contraseña'])),
                    is_active=True,
                )
                creados += 1

            messages.success(request, f"✅ {creados} usuarios creados correctamente.")

        except Exception as e:
            messages.error(request, f"❌ Error al procesar el archivo: {e}")

        return redirect('lista_usuarios')

    return redirect('lista_usuarios')
