import django_filters
from django import forms

from rehabilitacion.models import Informe, TipoInforme
from administracion.models import Profesional, ProfesionalArea


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