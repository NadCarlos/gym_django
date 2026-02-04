import django_filters
from django.db.models import Q

from finanzas.models import Factura, OrdenPago, Beneficiario


class FacturasFilter(django_filters.FilterSet):

    fecha = django_filters.DateFromToRangeFilter()
    id_beneficiario__nombre = django_filters.CharFilter(lookup_expr='icontains')
    id_paciente__apellido = django_filters.CharFilter(lookup_expr='icontains')
    id_beneficiario__numero_cuit = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Factura
        fields = [
            'fecha',
            'id_beneficiario__nombre',
            'id_paciente__apellido',
            'id_beneficiario__numero_cuit',
        ]

    # La forma vieja, para sacar solo un mes unico
    """def filter_by_month_year(self, queryset, name, value):
        try:
            year, month, day = value.split('-')
            return queryset.filter(
                Q(fecha__month=month) & Q(fecha__year=year)
            )
        except ValueError:
            return queryset"""
    

class OrdenesPagoFilter(django_filters.FilterSet):

    fecha = django_filters.DateFromToRangeFilter()
    id_beneficiario__nombre = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = OrdenPago
        fields = [
            'fecha',
            'id_beneficiario__nombre',
        ]


class BeneficiarioFilter(django_filters.FilterSet):

    nombre = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Beneficiario
        fields = [
            'nombre',
        ]
