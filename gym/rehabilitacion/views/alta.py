from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse

import json

from rehabilitacion.forms import (
    AltaCreateForm,
    AltaTerminateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.diagnostico_etiologico import DiagnosticoEtiologicoRepository


pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
diagnosticoEtiologicoRepo = DiagnosticoEtiologicoRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        diagnosticos_etiologicos = diagnosticoEtiologicoRepo.get_all_dict()
        form = AltaCreateForm(initial={'id_paciente_rehabilitacion':id_paciente_rehabilitacion.id})
        return render(
            request,
            'alta/create.html',
            dict(
                form=form,
                diagnosticos_json=json.dumps(diagnosticos_etiologicos),
            )
        )
    
    def post(self, request, id):
        form = AltaCreateForm(request.POST)
        if form.is_valid():
            fecha=form.cleaned_data['fecha']
            id_paciente_rehabilitacion=form.cleaned_data['id_paciente_rehabilitacion']
            id_diagnostico_etiologico=form.cleaned_data['id_diagnostico_etiologico']
            alta_nueva=altaRepo.create(
                fecha=fecha,
                id_diagnostico_etiologico=id_diagnostico_etiologico,
                id_paciente_rehabilitacion=id_paciente_rehabilitacion,
            )

            return redirect('paciente_rehab_detail', id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaDetail(View):

    def get(self, request, id):
        alta = altaRepo.filter_by_id(id=id)
        return render(
            request,
            'alta/detail.html',
            dict(
                alta=alta,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaTerminate(View):

    def get(self, request, id):
        form = AltaTerminateForm(initial={"dado_alta":True})
        return render(
            request,
            'alta/terminate.html',
            dict(
                form=form,
            )
        )

    def post(self, request, id):
        alta = altaRepo.get_by_id(id=id)
        form = AltaTerminateForm(request.POST)
        if form.is_valid():
            fecha_alta=form.cleaned_data['fecha_alta']
            dado_alta=form.cleaned_data['dado_alta']
            alta_terminated = altaRepo.terminate(
                alta=alta,
                fecha_alta=fecha_alta,
                dado_alta=dado_alta,
            )

            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id )

class DiagnosticoEtiologicoByTipoDiscapacidadView(View):
    def get(self, request, tipo_discapacidad_id):
        diagnosticos_etiologicos = diagnosticoEtiologicoRepo.filter_by_tipo_discapacidad_id_list(id_tipo_discapacidad=tipo_discapacidad_id)
        return JsonResponse(list(diagnosticos_etiologicos), safe=False)
