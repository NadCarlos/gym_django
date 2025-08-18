from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse

from rehabilitacion.forms import (
    AltaCreateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.diagnostico import DiagnosticoRepository
from rehabilitacion.repositories.familia import FamiliaRepository


pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
diagnosticoRepo = DiagnosticoRepository()
familiaRepo = FamiliaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        form = AltaCreateForm(initial={'id_paciente_rehabilitacion':id_paciente_rehabilitacion.id})
        return render(
            request,
            'alta/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request, id):
        form = AltaCreateForm(request.POST)
        if form.is_valid():
            fecha=form.cleaned_data['fecha']
            id_paciente_rehabilitacion=form.cleaned_data['id_paciente_rehabilitacion']
            id_diagnostico=form.cleaned_data['id_diagnostico']
            alta_nueva=altaRepo.create(
                fecha=fecha,
                id_diagnostico=id_diagnostico,
                id_paciente_rehabilitacion=id_paciente_rehabilitacion,
            )

            return redirect('alta_detail', alta_nueva.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaDetail(View):

    def get(self, request, id):
        alta = altaRepo.filter_by_id(id=id)
        print(alta)
        return render(
            request,
            'alta/detail.html',
            dict(
                alta=alta,
            )
        )


class DiagnosticosByFamiliaView(View):
    def get(self, request, familia_id):
        diagnosticos = diagnosticoRepo.filter_by_familia_id_list(id_familia=familia_id)
        return JsonResponse(list(diagnosticos), safe=False)
