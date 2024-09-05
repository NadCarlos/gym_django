import django_filters
from django import forms

from administracion.models import Paciente, Asistencia


class PacienteFilter(django_filters.FilterSet):
    apellido = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Paciente
        fields = {
            'apellido',
            'id_obra_social',
            'id_estado_civil',
            'id_sexo',
            }

class AsistenciasFilter(django_filters.FilterSet):
    fecha = django_filters.DateFromToRangeFilter()

    id_prestacion_paciente__id_paciente__apellido = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Asistencia
        fields = ['fecha', 'id_prestacion_paciente__id_paciente__apellido']