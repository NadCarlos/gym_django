from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.decorators import requiere_areas

import json

from rehabilitacion.forms import (
    AltaCreateForm,
    AltaTerminateForm,
    AltaFuncionalCreateForm,
    DiagnosticoFuncionalCreateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.diagnostico_etiologico import DiagnosticoEtiologicoRepository
from rehabilitacion.repositories.diagnostico_funcional import DiagnosticoFuncionalRepository
from rehabilitacion.repositories.alta_funcional import AltaFuncionalRepository


pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
diagnosticoEtiologicoRepo = DiagnosticoEtiologicoRepository()
diagnosticoFuncionalRepo = DiagnosticoFuncionalRepository()
altaFuncionalRepo = AltaFuncionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTerminate(View):

    def get(self, request, id):
        form = AltaTerminateForm(initial={"dado_alta":True})
        alta = altaRepo.get_by_id(id=id)
        return render(
            request,
            'alta/terminate.html',
            dict(
                form=form,
                alta=alta,
            )
        )

    def post(self, request, id):
        alta = altaRepo.get_by_id(id=id)
        form = AltaTerminateForm(request.POST)
        if form.is_valid():
            fecha_alta=form.cleaned_data['fecha_alta']
            dado_alta=form.cleaned_data['dado_alta']
            altas_funcionales = altaFuncionalRepo.filter_by_alta_id(alta_id=alta.id)
            for alta_funcional in altas_funcionales:
                altaFuncionalRepo.delete_by_activo(
                    alta_funcional=alta_funcional,
                )
            alta_terminated = altaRepo.terminate(
                alta=alta,
                fecha_alta=fecha_alta,
                dado_alta=dado_alta,
            )

            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id )


@method_decorator(login_required(login_url='login'), name='dispatch')
class DiagnosticoEtiologicoByTipoDiscapacidadView(View):

    def get(self, request, tipo_discapacidad_id):
        diagnosticos_etiologicos = diagnosticoEtiologicoRepo.filter_by_tipo_discapacidad_id_list(id_tipo_discapacidad=tipo_discapacidad_id)
        return JsonResponse(list(diagnosticos_etiologicos), safe=False)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalCreate(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        diagnosticos_funcionales = diagnosticoFuncionalRepo.filter_by_tipo_diagnostico_etiologico_id_list(id_diagnostico_etiologico=alta.id_diagnostico_etiologico.id)
        form = AltaFuncionalCreateForm(initial={'id_usuario': request.user, 'id_alta': alta})

        return render(
            request,
            'alta_funcional/create.html',
            dict(
                form=form,
                diagnosticos_funcionales = diagnosticos_funcionales,
                alta=alta,
            )
        )
    
    def post(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        diagnosticos_funcionales = diagnosticoFuncionalRepo.filter_by_tipo_diagnostico_etiologico_id_list(id_diagnostico_etiologico=alta.id_diagnostico_etiologico.id)
        form = AltaFuncionalCreateForm(request.POST)
        diagnostico_funcional_id = request.POST.get('select-diagnostico-funcional')

        if not diagnostico_funcional_id:
            return render(
                request,
                'alta_funcional/create.html',
                dict(
                    form=form,
                    diagnosticos_funcionales=diagnosticos_funcionales,
                    alta=alta,
                    selected_diagnostico_funcional_id='',
                    error_message='Debe seleccionar un diagnóstico funcional.',
                ),
            )

        diagnostico_funcional_id_int = int(diagnostico_funcional_id)
        diagnostico_funcional = diagnosticoFuncionalRepo.filter_by_id(diagnostico_funcional_id_int)
        if form.is_valid():
            id_alta=form.cleaned_data['id_alta']
            observaciones=form.cleaned_data['observaciones']
            id_usuario=form.cleaned_data['id_usuario']

            altaFuncionalRepo.create(
                id_alta=id_alta,
                id_diagnostico_funcional=diagnostico_funcional,
                observaciones=observaciones,
                id_usuario=id_usuario,
            )
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalList(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        altas_funcionales = altaFuncionalRepo.filter_by_alta_id(alta_id=alta.id)
        paciente = pacienteRepo.get_by_id(id=alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)

        return render(
            request,
            'alta_funcional/list.html',
            dict(
                altas_funcionales = altas_funcionales,
                alta=alta,
                paciente=paciente,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalUpdate(View):

    def get(self, request, alta_funcional_id):
        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_funcional_id)
        alta = alta_funcional.id_alta
        diagnosticos_funcionales = diagnosticoFuncionalRepo.filter_by_tipo_diagnostico_etiologico_id_list(
            id_diagnostico_etiologico=alta.id_diagnostico_etiologico.id,
        )

        form = AltaFuncionalCreateForm(initial={
            'id_usuario': request.user,
            'id_alta': alta,
            'observaciones': alta_funcional.observaciones,
        })

        return render(
            request,
            'alta_funcional/update.html',
            dict(
                form=form,
                alta=alta,
                alta_funcional=alta_funcional,
                diagnosticos_funcionales=diagnosticos_funcionales,
            ),
        )

    def post(self, request, alta_funcional_id):
        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_funcional_id)
        alta = alta_funcional.id_alta

        diagnostico_funcional_id = request.POST.get('select-diagnostico-funcional')
        if not diagnostico_funcional_id:
            return redirect('alta_funcional_update', alta_funcional_id=alta_funcional.id)

        diagnostico_funcional = diagnosticoFuncionalRepo.filter_by_id(int(diagnostico_funcional_id))
        if not diagnostico_funcional:
            return redirect('alta_funcional_update', alta_funcional_id=alta_funcional.id)

        form = AltaFuncionalCreateForm(request.POST)
        if form.is_valid():
            observaciones = form.cleaned_data['observaciones']
            altaFuncionalRepo.update(
                alta_funcional=alta_funcional,
                id_diagnostico_funcional=diagnostico_funcional,
                observaciones=observaciones,
            )

        return redirect('alta_funcional_list', alta_id=alta.id)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoFuncionalRemove(View):

    def get(self, request, alta_id):

        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_id)
        altaFuncionalRepo.delete_by_activo(alta_funcional=alta_funcional)
        return redirect('alta_funcional_list', alta_funcional.id_alta.id )
