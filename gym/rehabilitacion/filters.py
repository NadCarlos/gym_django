import django_filters
from django import forms

from rehabilitacion.models import Informe, Situacion, TipoInforme
from administracion.models import Paciente, Profesional, ProfesionalArea


class PacienteRehabFilter(django_filters.FilterSet):
    apellido = django_filters.CharFilter(lookup_expr="icontains")
    numero_dni = django_filters.CharFilter(lookup_expr="icontains")

    situacion = django_filters.ModelChoiceFilter(
        queryset=Situacion.objects.all().order_by("nombre"),
        method="filter_situacion",
        label="Situacion",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.form.fields.values():
            field.widget.attrs.update({
                "class": "form-control custom-class"
            })

    def filter_situacion(self, queryset, name, value):
        if value is None:
            return queryset

        return queryset.filter(
            ultima_situacion_id=value.pk
        )

    class Meta:
        model = Paciente
        fields = [
            "apellido",
            "id_obra_social",
            "id_estado_civil",
            "id_sexo",
            "numero_dni",
            "situacion",
        ]


class InformeFilter(django_filters.FilterSet):
    fecha = django_filters.DateFilter(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    id_tipo_informe = django_filters.ModelChoiceFilter(
        queryset=TipoInforme.objects.all().order_by("nombre"),
        widget=forms.Select(attrs={"class": "form-control custom-class"}),
    )
    id_profesional = django_filters.ModelChoiceFilter(
        queryset=Profesional.objects.filter(
            id__in=ProfesionalArea.objects.filter(id_area=2).values_list(
                "id_profesional", flat=True
            ),
            activo=True,
        ).order_by("apellido"),
        widget=forms.Select(attrs={"class": "form-control custom-class"}),
    )

    class Meta:
        model = Informe
        fields = [
            "fecha",
            "id_tipo_informe",
            "id_profesional",
        ]
