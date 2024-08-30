import django_filters
from django import forms

from administracion.models import Paciente


class PacienteFilter(django_filters.FilterSet):
    apellido = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Paciente
        fields = {
            'apellido',
            'id_obra_social',
            'id_estado_civil',
            'id_sexo'
            }
        

    