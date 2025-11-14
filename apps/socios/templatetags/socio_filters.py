from django import template
from apps.socios.models import Socio

register = template.Library()

@register.filter
def get_socio_id(socios, rut_usuario):
    """
    Busca el ID del socio cuyo RUT coincide con el usuario logeado.
    Retorna None si no lo encuentra.
    """
    socio = socios.filter(rut=rut_usuario).first()
    return socio.id if socio else None
