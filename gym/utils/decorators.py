from functools import wraps
from django.http import HttpResponseForbidden


def requiere_areas(*areas):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return HttpResponseForbidden("Debe iniciar sesión")

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not user.groups.filter(name__in=areas).exists():
                return HttpResponseForbidden("Acceso denegado")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator