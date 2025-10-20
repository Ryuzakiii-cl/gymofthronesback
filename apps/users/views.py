from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect, render




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
