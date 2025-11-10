def formatear_rut(rut):
    """Formatea un RUT chileno sin puntos ni guion -> con puntos y guion."""
    try:
        rut = str(rut)
        cuerpo, dv = rut[:-1], rut[-1]
        cuerpo_con_puntos = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_con_puntos}-{dv.upper()}"
    except Exception:
        return rut  # si viene vacío o mal formado, se deja igual


def formatear_numero(valor):
    """Convierte número a formato chileno: 1.234.567"""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"

