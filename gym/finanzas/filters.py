import django_filters
from django.db.models import Q

from finanzas.models import Factura, Beneficiario


class FacturasFilter(django_filters.FilterSet):

    fecha = django_filters.CharFilter(method='filter_by_month_year')
    id_beneficiario__nombre = django_filters.CharFilter(lookup_expr='icontains')
    id_beneficiario__numero_cuit = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Factura
        fields = [
            'fecha',
            'id_beneficiario__nombre',
            'id_beneficiario__numero_cuit',
        ]

    def filter_by_month_year(self, queryset, name, value):
        try:
            year, month, day = value.split('-')
            return queryset.filter(
                Q(fecha__month=month) & Q(fecha__year=year)
            )
        except ValueError:
            return queryset