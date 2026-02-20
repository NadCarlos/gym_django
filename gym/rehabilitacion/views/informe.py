from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.decorators import requiere_areas

from rehabilitacion.repositories.informe import InformeRepository
from administracion.repositories.paciente import PacienteRepository

from rehabilitacion.models import Informe


informeRepo = InformeRepository()
pacienteRepo = PacienteRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformesList(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        informes = informeRepo.filter_by_paciente_id(paciente_id=id)
        return render(
            request,
            'informes/list.html',
            dict(
                paciente=paciente,
                informes=informes,
            )
        )


