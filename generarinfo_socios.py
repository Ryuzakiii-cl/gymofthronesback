import os
import django
import random
from datetime import datetime, timedelta

# --- Configurar Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymofthronesback.settings')  # ← reemplaza con el nombre real de tu settings
django.setup()

from apps.socios.models import Socio
from apps.planes.models import Plan, SocioPlan

# --- Funciones auxiliares ---
def calcular_dv(rut_sin_dv):
    rut_reverso = str(rut_sin_dv)[::-1]
    multiplicador = 2
    suma = 0
    for digito in rut_reverso:
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    resto = suma % 11
    dv = 11 - resto
    if dv == 11:
        return '0'
    elif dv == 10:
        return 'K'
    else:
        return str(dv)

def generar_rut_chileno():
    cuerpo_rut = random.randint(7000000, 26999999)
    dv = calcular_dv(cuerpo_rut)
    return f"{cuerpo_rut}-{dv}"

# --- Datos base ---
nombres = [
    "Juan", "María", "Pedro", "Ana", "Luis", "Camila", "Diego", "Sofía",
    "Carlos", "Valentina", "Javier", "Isidora", "Miguel", "Fernanda", "José"
]
apellidos = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva",
    "Martínez", "Sepúlveda", "Morales", "Rodríguez", "Fuentes", "Hernández", "Torres"
]
formas_pago = ["Efectivo", "Tarjeta", "Transferencia"]

# --- Planes reales desde BD ---
planes = list(Plan.objects.all())
if not planes:
    print("⚠️ No hay planes en la base de datos. Agrega algunos antes de ejecutar este script.")
    exit()

# --- Parámetros ---
TOTAL_SOCIOS = 100
ruts_generados = set()

# --- Generación ---
for _ in range(TOTAL_SOCIOS):
    rut = generar_rut_chileno()
    while rut in ruts_generados or Socio.objects.filter(rut=rut).exists():
        rut = generar_rut_chileno()
    ruts_generados.add(rut)

    nombre = random.choice(nombres)
    apellido_paterno = random.choice(apellidos)
    apellido_materno = random.choice(apellidos) if random.random() > 0.2 else ""
    correo = f"{nombre.lower()}.{apellido_paterno.lower()}{random.randint(1, 99)}@correo.cl"
    telefono = f"+569{random.randint(40000000, 99999999)}"

    edad_dias = random.randint(18 * 365, 70 * 365)
    fecNac = (datetime.now() - timedelta(days=edad_dias)).date()
    estado = random.choice([True, False])

    # Crear socio
    socio = Socio.objects.create(
        rut=rut,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        correo=correo,
        telefono=telefono,
        fecNac=fecNac,
        estado=estado,
    )

    # Asignar plan al azar (exactamente como en el formulario)
    plan = random.choice(planes)
    forma_pago = random.choice(formas_pago)

    SocioPlan.objects.create(
        socio=socio,
        plan=plan,
        forma_pago=forma_pago,
        fecInicio=datetime.now().date(),
        fecFin=(datetime.now() + timedelta(days=plan.duracion)).date() if hasattr(plan, 'duracion') else None,
        monto_pagado=plan.precio if hasattr(plan, 'precio') else 0,
        estado=True
    )

print(f"✅ Se generaron {TOTAL_SOCIOS} socios con sus planes asignados correctamente.")
