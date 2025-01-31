from django.urls import path

from finanzas.views.libro_ventas import (
    Index,
    CargaView,
    FacturasList,
    BeneficiariosList,
    BeneficiarioUpdate,
)


urlpatterns = [
    path(route='index/',view=Index.as_view(), name='index'),
    path(route='upload/',view=CargaView.as_view(), name='upload'),
    path(route='list/',view=FacturasList.as_view(), name='list'),
    path(route='beneficiarios_list/',view=BeneficiariosList.as_view(), name='beneficiarios_list'),
    path(route='<int:id>/beneficiario_update/',view=BeneficiarioUpdate.as_view(), name='beneficiario_update'),
]