from django.urls import path

from finanzas.views.libro_ventas import (
    CargaView,
    GuardarCarga,
)


urlpatterns = [
    path(route='upload/',view=CargaView.as_view(), name='upload'),
    path(route='save/',view=GuardarCarga.as_view(), name='save'),
]