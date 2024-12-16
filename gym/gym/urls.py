from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("administracion/", include("administracion.urls")),
    path("entrada/", include("entrada.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("finanzas/", include("finanzas.urls")),
    path("", include("home.urls")),
]
