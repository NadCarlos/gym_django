from django.contrib.auth.models import User

def es_admin_o_finanzas(user: User) -> bool:
    return user.is_superuser or user.groups.filter(name="Finanzas").exists()

def es_admin_o_gimnasio(user: User) -> bool:
    return user.is_superuser or user.groups.filter(name="Gimnasio").exists()

def es_admin_o_rehabilitacion(user: User) -> bool:
    return user.is_superuser or user.groups.filter(name="Rehabilitacion").exists()