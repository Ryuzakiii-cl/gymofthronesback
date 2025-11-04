import csv
import random

def calcular_dv(rut_sin_dv):
    """
    Calcula el Dígito Verificador (DV) de un RUT chileno.
    """
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
    """
    Genera un cuerpo de RUT aleatorio (7 u 8 dígitos) y le añade su DV.
    Esto cumple con tu requisito de "8 o 9 números de largo" (contando el DV).
    """
    # Rango para 7 u 8 dígitos (de 1.000.000 a 99.999.999)
    cuerpo_rut = random.randint(7000000, 26999999)
    dv = calcular_dv(cuerpo_rut)
    return f"{cuerpo_rut}{dv}"

# --- Listas de datos falsos ---
nombres = [
    "Juan", "María", "Pedro", "Ana", "Luis", "Camila", "Diego", "Sofía", "Carlos", "Valentina",
    "Javier", "Isidora", "Miguel", "Fernanda", "José", "Antonia", "Andrés", "Constanza", "Felipe", "Martina",
    "Vicente", "Catalina", "Sebastián", "Francisca", "Matías", "Javiera", "Tomás", "Daniela", "Benjamín", "Paz"
]

apellidos = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva", "Martínez", "Sepúlveda",
    "Morales", "Rodríguez", "López", "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza", "Valenzuela",
    "Castillo", "Ramírez", "Reyes", "Gutiérrez", "Castro", "Vargas", "Álvarez", "Vásquez", "Tapia", "Fernández"
]

# --- Constantes definidas ---
CONTRASENA_FIJA = "Contraseñadeprueba00."
TOTAL_USUARIOS = 50
NUM_ADMINS = 2
NOMBRE_ARCHIVO = "usuarios_generados.csv"

# --- Generación de datos ---

# Crear la lista de roles (2 admin, 48 socios)
roles = ["admin"] * NUM_ADMINS + ["profesor"] * (TOTAL_USUARIOS - NUM_ADMINS)
# Barajar los roles para que los admins no sean siempre los primeros
random.shuffle(roles)

datos_para_csv = []
ruts_generados = set() # Para asegurar que no haya RUTs duplicados

# Agregar encabezados
datos_para_csv.append(["rut", "nombre", "apellido", "correo", "rol", "contraseña"])

print(f"Generando {TOTAL_USUARIOS} usuarios...")

i = 0
while i < TOTAL_USUARIOS:
    rut = generar_rut_chileno()
    
    # Asegurarnos de que el RUT no se repita
    if rut in ruts_generados:
        continue
    ruts_generados.add(rut)
    
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    
    # Crear correo simple y añadir un número aleatorio para evitar duplicados
    correo = f"{nombre.lower()}.{apellido.lower()}{random.randint(1, 99)}@dominiofalso.cl"
    
    rol = roles[i]
    
    # Añadir la fila
    datos_para_csv.append([
        rut,
        nombre,
        apellido,
        correo,
        rol,
        CONTRASENA_FIJA
    ])
    
    i += 1

# --- Escritura del archivo CSV ---
try:
    with open(NOMBRE_ARCHIVO, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(datos_para_csv)
    
    print(f"\n¡Éxito! Se ha creado el archivo '{NOMBRE_ARCHIVO}' con {TOTAL_USUARIOS} usuarios.")
    print(f"({NUM_ADMINS} admin, {TOTAL_USUARIOS - NUM_ADMINS} socios)")

except IOError as e:
    print(f"\nError: No se pudo escribir el archivo. {e}")