from django.urls import path

from finanzas.views.libro_ventas import (
    Index,
    CargaView,
    FacturasList,
    BeneficiariosList,
    BeneficiarioUpdate,
    OrdenPagoCreate,
    OrdenPagoPopulate,
    OrdenPagoDetail,
    OrdenesPagoList,
    OrdenPagoDelete,
)


urlpatterns = [
    path(route='',view=Index.as_view(), name='index'),
    path(route='upload/',view=CargaView.as_view(), name='upload'),
    path(route='list/',view=FacturasList.as_view(), name='list'),
    path(route='beneficiarios_list/',view=BeneficiariosList.as_view(), name='beneficiarios_list'),
    path(route='<int:id>/beneficiario_update/',view=BeneficiarioUpdate.as_view(), name='beneficiario_update'),
    path(route='orden_pago_create/',view=OrdenPagoCreate.as_view(), name='orden_pago_create'),
    path(route='<int:id>/orden_pago_populate/',view=OrdenPagoPopulate.as_view(), name='orden_pago_populate'),
    path(route='<int:id>/detail/',view=OrdenPagoDetail.as_view(), name='detail'),
    path(route='orden_pago_list/',view=OrdenesPagoList.as_view(), name='orden_pago_list'),
    path(route='<int:id>/orden_pago_delete/',view=OrdenPagoDelete.as_view(), name='orden_pago_delete'),
]