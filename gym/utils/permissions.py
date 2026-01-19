from django.contrib.auth.models import User

def tiene_area(user: User, *areas: str) -> bool:
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=areas).exists()


def solo_areas(user: User, permitidas: list[str]) -> bool:
    if user.is_superuser:
        return True

    grupos_usuario = set(user.groups.values_list("name", flat=True))
    return grupos_usuario.issubset(set(permitidas))
