from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from finanzas.models import Beneficiario, DetalleOrden, Factura, OrdenPago
from finanzas.repositories.facturas import FacturaRepository


class FacturaListQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="finance-query")
        cls.beneficiario = Beneficiario.objects.create(
            nombre="Prestador",
            numero_cuit="20123456789",
        )
        cls.factura_pagada = Factura.objects.create(
            tipo="A",
            pto_vta="1",
            numero="1",
            fecha=date(2026, 1, 1),
            importe=100,
            id_beneficiario=cls.beneficiario,
        )
        cls.factura_impaga = Factura.objects.create(
            tipo="A",
            pto_vta="1",
            numero="2",
            fecha=date(2026, 1, 2),
            importe=200,
            id_beneficiario=cls.beneficiario,
        )
        orden = OrdenPago.objects.create(
            fecha=date(2026, 1, 3),
            numero="OP-1",
            id_beneficiario=cls.beneficiario,
            id_usuario=cls.user,
        )
        DetalleOrden.objects.create(
            id_ordenpago=orden,
            id_factura=cls.factura_pagada,
            importe=100,
        )

    def test_list_query_preloads_display_and_payment_relations(self):
        with self.assertNumQueries(2):
            facturas = list(FacturaRepository().get_all_for_list())
            [
                (
                    factura.id_beneficiario.nombre,
                    factura.id_paciente,
                    factura.tiene_orden_pago,
                    [
                        detalle.id_ordenpago.fecha
                        for detalle in factura.detalles_orden_pago
                    ],
                )
                for factura in facturas
            ]

    def test_balance_query_and_discount_total_have_constant_query_counts(self):
        from finanzas.repositories.descuentos import DescuentoRepository

        with self.assertNumQueries(1):
            facturas = list(FacturaRepository().get_all_for_balance())
            [
                (
                    factura.id_beneficiario.nombre,
                    factura.tiene_orden_pago,
                )
                for factura in facturas
            ]

        with self.assertNumQueries(1):
            self.assertEqual(DescuentoRepository().total_activo(), 0)

