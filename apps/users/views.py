from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect, render
from .models import Usuario
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect 


# --- LOGIN ---
def login_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut').strip()
        password = request.POST.get('password')

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
                messages.warning(request, "Tu cuenta no tiene rol asignado.")
                return redirect('login')
        else:
            messages.error(request, "❌ RUT o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'users/login.html')

# --- LOGOUT ---
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')


# --- DASHBOARDS POR ROL ---
@login_required
def dashboard_superadmin(request):
    return render(request, 'users/dashboard_superadmin.html')

@login_required
def dashboard_admin(request):
    return render(request, 'users/dashboard_admin.html')

@login_required
def dashboard_profesor(request):
    return render(request, 'users/dashboard_profesor.html')

@login_required
def dashboard_socio(request):
    return render(request, 'users/dashboard_socio.html')



def error_404(request, exception=None):
    """Página personalizada para errores 404"""
    return render(request, 'users/404.html', status=404)




def es_superadmin(user):
    return user.is_authenticated and user.rol == 'superadmin'


@login_required
@user_passes_test(es_superadmin)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'nombre')
    return render(request, 'users/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(es_superadmin)
def crear_usuario(request):
    if request.method == 'POST':
        rut = request.POST['rut']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        rol = request.POST['rol']
        password = request.POST['password']

        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, "❌ Ya existe un usuario con ese RUT.")
            return redirect('crear_usuario')

        Usuario.objects.create_user(
            rut=rut,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            rol=rol,
            password=password
        )
        messages.success(request, f"✅ Usuario {nombre} creado correctamente.")
        return redirect('lista_usuarios')

    return render(request, 'users/form_usuario.html', {'titulo': 'Crear Usuario'})


@login_required
@user_passes_test(es_superadmin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.nombre = request.POST['nombre']
        usuario.apellido = request.POST['apellido']
        usuario.correo = request.POST['correo']
        usuario.rol = request.POST['rol']
        usuario.is_active = 'is_active' in request.POST
        usuario.save()
        messages.success(request, "✅ Usuario actualizado correctamente.")
        return redirect('lista_usuarios')

    return render(request, 'users/form_usuario.html', {'usuario': usuario, 'titulo': 'Editar Usuario'})


@login_required
@user_passes_test(es_superadmin)
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    messages.success(request, "🗑️ Usuario eliminado correctamente.")
    return redirect('lista_usuarios')
