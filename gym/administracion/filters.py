import django_filters

from administracion.models import Paciente, Asistencia, ObraSocial, Prestacion, Profesional, Cuota, DetallePago, TipoPago


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
    id_prestacion_paciente__id_obra_social = django_filters.ModelChoiceFilter(
        queryset = ObraSocial.objects.filter(activo=True)
    )
    id_prestacion_paciente__id_prestacion = django_filters.ModelChoiceFilter(
        queryset = Prestacion.objects.filter(activo=True)
    )

    class Meta:
        model = Asistencia
        fields = [
            'fecha',
            'id_prestacion_paciente__id_paciente__apellido',
            'id_prestacion_paciente__id_obra_social',
            'id_prestacion_paciente__id_prestacion'
        ]


class ProfesionalFilter(django_filters.FilterSet):
    apellido = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Profesional
        fields = {
            'apellido',
            'id_sexo'
            }
        

class CuotaFilter(django_filters.FilterSet):

    imputado = django_filters.DateFromToRangeFilter()
    id_paciente_plan__id_paciente__apellido = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Cuota
        fields = {
            'imputado',
            'id_paciente_plan__id_paciente__apellido'
            }
        

class DetallePagoFilter(django_filters.FilterSet):

    id_pago__fecha = django_filters.DateFromToRangeFilter()
    id_pago__id_tipo_pago__nombre = django_filters.ModelChoiceFilter(queryset = TipoPago.objects.filter(activo=True))

    class Meta:
        model = DetallePago
        fields = {
            'id_pago__fecha',
            'id_pago__id_tipo_pago__nombre',
            }