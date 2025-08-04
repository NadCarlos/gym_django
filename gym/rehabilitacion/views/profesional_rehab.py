import pandas as pd
import io

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from administracion.models import Profesional

from administracion.filters import ProfesionalFilter

from administracion.forms import (
    ProfesionalCreateForm,
    ProfesionalUpdateForm,
    )

from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.sexo import SexoRepository
from administracion.repositories.localidad import LocalidadRepository
from administracion.repositories.profesional_area import ProfesionalAreaRepository

profesionalRepo = ProfesionalRepository()
sexoRepo = SexoRepository()
localidadRepo = LocalidadRepository()
profesionalAreaRepo = ProfesionalAreaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalRehabList(View):
    template_name = 'profesional_rehab/list.html'
    context_object_name = 'profesional_rehab'

    def get(self, request):

        filterset = ProfesionalFilter(request.GET, profesionalRepo.filter_profesional_area(id_area=2))
        
        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        # Obtener el queryset filtrado
        profesionales = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            profesionales = filterset.qs.order_by(ordering)

        profesionales_count = profesionales.count()

        return render(
            request,
            self.template_name,
            dict(
                profesionales=profesionales,
                profesionales_count=profesionales_count,
                form=filterset.form,
                ordering=ordering,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalRehabDetail(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        return render(
            request,
            'profesional_rehab/detail.html',
            dict(
                profesional=profesional,
            )
        )