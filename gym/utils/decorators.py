from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def requiere_areas(*areas_permitidas):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("login")

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if user.groups.filter(name__in=areas_permitidas).exists():
                return view_func(request, *args, **kwargs)

            if user.groups.filter(name="Gimnasio").exists():
                return redirect("inicio")

            if user.groups.filter(name="Rehabilitacion").exists():
                return redirect("inicio_rehab")

            return HttpResponseForbidden("Acceso denegado")

        return _wrapped_view
    return decorator