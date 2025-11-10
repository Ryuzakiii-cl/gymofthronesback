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
