from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("administracion/", include("administracion.urls")),
    path("entrada/", include("entrada.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("finanzas/", include("finanzas.urls")),
    path("rehabilitacion/", include("rehabilitacion.urls")),
    path("", include("home.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)