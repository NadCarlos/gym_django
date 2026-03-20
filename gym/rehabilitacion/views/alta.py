from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from utils.decorators import requiere_areas

from rehabilitacion.forms import (
    AltaCreateForm,
    AltaEtiologicoCreateForm,
    AltaFuncionalCreateForm,
    AltaTerminateForm,
    AltaTipoDiscapacidadCreateForm,
)

from administracion.repositories.paciente import PacienteRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.alta_etiologico import AltaEtiologicoRepository
from rehabilitacion.repositories.alta_funcional import AltaFuncionalRepository
from rehabilitacion.repositories.alta_tipo_discapacidad import AltaTipoDiscapacidadRepository
from rehabilitacion.repositories.diagnostico_etiologico import DiagnosticoEtiologicoRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository


pacienteRepo = PacienteRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
diagnosticoEtiologicoRepo = DiagnosticoEtiologicoRepository()
altaFuncionalRepo = AltaFuncionalRepository()
altaTipoDiscapacidadRepo = AltaTipoDiscapacidadRepository()
altaEtiologicoRepo = AltaEtiologicoRepository()




@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)

        form = AltaCreateForm(initial={'id_paciente_rehabilitacion': paciente_rehabilitacion.id})
        return render(
            request,
            'alta/create.html',
            dict(
                form=form,
                paciente=paciente
            )
        )

    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)

        form = AltaCreateForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            diagnosticos_etiologicos = list(form.cleaned_data['diagnosticos_etiologicos'])
            tipos_discapacidad = list(form.cleaned_data['tipos_discapacidad'])

            with transaction.atomic():
                alta_nueva = altaRepo.create(
                    fecha=fecha,
                    id_paciente_rehabilitacion=paciente_rehabilitacion,
                )

                for tipo_discapacidad in tipos_discapacidad:
                    altaTipoDiscapacidadRepo.create(
                        id_alta=alta_nueva,
                        id_tipo_discapacidad=tipo_discapacidad,
                        observaciones='',
                        id_usuario=request.user,
                    )

                for diagnostico_etiologico in diagnosticos_etiologicos:
                    altaEtiologicoRepo.create(
                        id_alta=alta_nueva,
                        id_diagnostico_etiologico=diagnostico_etiologico,
                        observaciones='',
                        id_usuario=request.user,
                    )

            messages.success(request, 'Alta creada correctamente.')
            return redirect('paciente_rehab_detail', paciente.id)

        return render(
            request,
            'alta/create.html',
            dict(
                form=form,
                paciente=paciente
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaDetail(View):

    def get(self, request, id):
        alta = altaRepo.filter_by_id(id=id)
        if alta is None:
            messages.error(request, 'No se encontró el alta.')
            return redirect('pacientes_rehab_list', True)

        altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_all_by_alta_id(alta_id=alta.id)
        altas_etiologicos = altaEtiologicoRepo.filter_all_by_alta_id(alta_id=alta.id)
        altas_funcionales = altaFuncionalRepo.filter_all_by_alta_id(alta_id=alta.id)
        return render(
            request,
            'alta/detail.html',
            dict(
                alta=alta,
                altas_tipo_discapacidad=altas_tipo_discapacidad,
                altas_etiologicos=altas_etiologicos,
                altas_funcionales=altas_funcionales,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTerminate(View):

    def get(self, request, id):
        form = AltaTerminateForm(initial={"dado_alta": True})
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
            fecha_alta = form.cleaned_data['fecha_alta']
            dado_alta = form.cleaned_data['dado_alta']
            altas_funcionales = altaFuncionalRepo.filter_by_alta_id(alta_id=alta.id)
            altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_by_alta_id(alta_id=alta.id)
            altas_etiologicos = altaEtiologicoRepo.filter_by_alta_id(alta_id=alta.id)

            with transaction.atomic():
                for alta_funcional in altas_funcionales:
                    altaFuncionalRepo.delete_by_activo(alta_funcional=alta_funcional)
                for alta_tipo_discapacidad in altas_tipo_discapacidad:
                    altaTipoDiscapacidadRepo.delete_by_activo(alta_tipo_discapacidad=alta_tipo_discapacidad)
                for alta_etiologico in altas_etiologicos:
                    altaEtiologicoRepo.delete_by_activo(alta_etiologico=alta_etiologico)

                altaRepo.terminate(
                    alta=alta,
                    fecha_alta=fecha_alta,
                    dado_alta=dado_alta,
                )

            messages.success(request, 'Alta finalizada correctamente.')
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class DiagnosticoEtiologicoByTipoDiscapacidadView(View):

    def get(self, request, tipo_discapacidad_id):
        diagnosticos_etiologicos = diagnosticoEtiologicoRepo.filter_by_tipo_discapacidad_id_list(
            id_tipo_discapacidad=tipo_discapacidad_id,
        )
        return JsonResponse(list(diagnosticos_etiologicos), safe=False)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTipoDiscapacidadCreate(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        form = AltaTipoDiscapacidadCreateForm(initial={'id_usuario': request.user, 'id_alta': alta})
        return render(
            request,
            'alta_tipo_discapacidad/create.html',
            dict(
                form=form,
                alta=alta,
            )
        )

    def post(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        form = AltaTipoDiscapacidadCreateForm(request.POST)
        if form.is_valid():
            tipo_discapacidad = form.cleaned_data['id_tipo_discapacidad']
            if altaTipoDiscapacidadRepo.exists_active_by_alta_and_tipo(
                alta_id=alta.id,
                tipo_discapacidad_id=tipo_discapacidad.id,
            ):
                return render(
                    request,
                    'alta_tipo_discapacidad/create.html',
                    dict(
                        form=form,
                        alta=alta,
                        error_message='Ese tipo de discapacidad ya está cargado para esta alta.',
                    )
                )

            altaTipoDiscapacidadRepo.create(
                id_alta=form.cleaned_data['id_alta'],
                id_tipo_discapacidad=tipo_discapacidad,
                observaciones=form.cleaned_data['observaciones'],
                id_usuario=form.cleaned_data['id_usuario'],
            )
            messages.success(request, 'Tipo de discapacidad agregado correctamente.')
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTipoDiscapacidadList(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_all_by_alta_id(alta_id=alta.id)
        paciente = pacienteRepo.get_by_id(id=alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)
        return render(
            request,
            'alta_tipo_discapacidad/list.html',
            dict(
                altas_tipo_discapacidad=altas_tipo_discapacidad,
                alta=alta,
                paciente=paciente,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTipoDiscapacidadUpdate(View):

    def get(self, request, alta_tipo_discapacidad_id):
        alta_tipo_discapacidad = altaTipoDiscapacidadRepo.get_by_id(id=alta_tipo_discapacidad_id)
        alta = alta_tipo_discapacidad.id_alta

        form = AltaTipoDiscapacidadCreateForm(
            instance=alta_tipo_discapacidad,
            initial={'id_usuario': alta_tipo_discapacidad.id_usuario or request.user, 'id_alta': alta},
        )
        return render(
            request,
            'alta_tipo_discapacidad/update.html',
            dict(
                form=form,
                alta=alta,
                alta_tipo_discapacidad=alta_tipo_discapacidad,
            )
        )

    def post(self, request, alta_tipo_discapacidad_id):
        alta_tipo_discapacidad = altaTipoDiscapacidadRepo.get_by_id(id=alta_tipo_discapacidad_id)
        alta = alta_tipo_discapacidad.id_alta

        form = AltaTipoDiscapacidadCreateForm(request.POST, instance=alta_tipo_discapacidad)
        if form.is_valid():
            tipo_discapacidad = form.cleaned_data['id_tipo_discapacidad']
            if altaTipoDiscapacidadRepo.exists_active_by_alta_and_tipo(
                alta_id=alta.id,
                tipo_discapacidad_id=tipo_discapacidad.id,
                exclude_alta_tipo_discapacidad_id=alta_tipo_discapacidad.id,
            ):
                return render(
                    request,
                    'alta_tipo_discapacidad/update.html',
                    dict(
                        form=form,
                        alta=alta,
                        alta_tipo_discapacidad=alta_tipo_discapacidad,
                        error_message='Ese tipo de discapacidad ya está cargado para esta alta.',
                    )
                )

            altaTipoDiscapacidadRepo.update(
                alta_tipo_discapacidad=alta_tipo_discapacidad,
                id_tipo_discapacidad=tipo_discapacidad,
                observaciones=form.cleaned_data['observaciones'],
            )
            messages.success(request, 'Tipo de discapacidad actualizado correctamente.')
            return redirect('alta_tipo_discapacidad_list', alta_id=alta.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaTipoDiscapacidadRemove(View):

    def get(self, request, alta_tipo_discapacidad_id):
        alta_tipo_discapacidad = altaTipoDiscapacidadRepo.get_by_id(id=alta_tipo_discapacidad_id)
        alta_id = alta_tipo_discapacidad.id_alta.id
        altaTipoDiscapacidadRepo.delete_by_activo(alta_tipo_discapacidad=alta_tipo_discapacidad)
        messages.success(request, 'Tipo de discapacidad quitado correctamente.')
        return redirect('alta_tipo_discapacidad_list', alta_id=alta_id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaEtiologicoCreate(View):

    template_name = 'alta_etiologico/create.html'

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)

        form = AltaEtiologicoCreateForm(initial={'id_usuario': request.user, 'id_alta': alta})
        return render(
            request,
            'alta_etiologico/create.html',
            dict(
                form=form,
                alta=alta,
            )
        )

    def post(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)

        form = AltaEtiologicoCreateForm(request.POST)
        if form.is_valid():
            diagnostico_etiologico = form.cleaned_data['id_diagnostico_etiologico']
            if altaEtiologicoRepo.exists_active_by_alta_and_diagnostico(
                alta_id=alta.id,
                diagnostico_etiologico_id=diagnostico_etiologico.id,
            ):
                return render(
                    request,
                    'alta_etiologico/create.html',
                    dict(
                        form=form,
                        alta=alta,
                        error_message='Ese diagnóstico etiológico ya está cargado para esta alta.',
                    )
                )

            altaEtiologicoRepo.create(
                id_alta=form.cleaned_data['id_alta'],
                id_diagnostico_etiologico=diagnostico_etiologico,
                observaciones=form.cleaned_data['observaciones'],
                id_usuario=form.cleaned_data['id_usuario'],
            )
            messages.success(request, 'Diagnóstico etiológico agregado correctamente.')
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaEtiologicoList(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        altas_etiologicos = altaEtiologicoRepo.filter_all_by_alta_id(alta_id=alta.id)
        paciente = pacienteRepo.get_by_id(id=alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)
        return render(
            request,
            'alta_etiologico/list.html',
            dict(
                altas_etiologicos=altas_etiologicos,
                alta=alta,
                paciente=paciente,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaEtiologicoUpdate(View):

    template_name = 'alta_etiologico/update.html'

    def get(self, request, alta_etiologico_id):
        alta_etiologico = altaEtiologicoRepo.get_by_id(id=alta_etiologico_id)
        alta = alta_etiologico.id_alta

        form = AltaEtiologicoCreateForm(
            instance=alta_etiologico,
            initial={'id_usuario': alta_etiologico.id_usuario or request.user, 'id_alta': alta},
        )
        return render(
            request,
            'alta_etiologico/update.html',
            dict(
                form=form,
                alta=alta,
                alta_etiologico=alta_etiologico,
            )
        )

    def post(self, request, alta_etiologico_id):
        alta_etiologico = altaEtiologicoRepo.get_by_id(id=alta_etiologico_id)
        alta = alta_etiologico.id_alta

        form = AltaEtiologicoCreateForm(request.POST, instance=alta_etiologico)
        if form.is_valid():
            diagnostico_etiologico = form.cleaned_data['id_diagnostico_etiologico']
            if altaEtiologicoRepo.exists_active_by_alta_and_diagnostico(
                alta_id=alta.id,
                diagnostico_etiologico_id=diagnostico_etiologico.id,
                exclude_alta_etiologico_id=alta_etiologico.id,
            ):
                return render(
                    request,
                    'alta_etiologico/update.html',
                    dict(
                        form=form,
                        alta=alta,
                        alta_etiologico=alta_etiologico,
                        error_message= 'Ese diagnóstico etiológico ya está cargado para esta alta.',
                    )
                )

            altaEtiologicoRepo.update(
                alta_etiologico=alta_etiologico,
                id_diagnostico_etiologico=diagnostico_etiologico,
                observaciones=form.cleaned_data['observaciones'],
            )
            messages.success(request, 'Diagnóstico etiológico actualizado correctamente.')
            return redirect('alta_etiologico_list', alta_id=alta.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaEtiologicoRemove(View):

    def get(self, request, alta_etiologico_id):
        alta_etiologico = altaEtiologicoRepo.get_by_id(id=alta_etiologico_id)
        alta_id = alta_etiologico.id_alta.id
        altaEtiologicoRepo.delete_by_activo(alta_etiologico=alta_etiologico)
        messages.success(request, 'Diagnóstico etiológico quitado correctamente.')
        return redirect('alta_etiologico_list', alta_id=alta_id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalCreate(View):

    template_name = 'alta_funcional/create.html'

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        if alta.dado_alta:
            messages.error(request, 'No se pueden agregar diagnósticos funcionales a un alta finalizada.')
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)

        form = AltaFuncionalCreateForm(initial={'id_usuario': request.user, 'id_alta': alta})
        return render(
            request,
            'alta_funcional/create.html',
            dict(
                form=form,
                alta=alta,
            )
        )

    def post(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)

        form = AltaFuncionalCreateForm(request.POST)
        if form.is_valid():
            diagnostico_funcional = form.cleaned_data['id_diagnostico_funcional']
            if altaFuncionalRepo.exists_active_by_alta_and_diagnostico(
                alta_id=alta.id,
                diagnostico_funcional_id=diagnostico_funcional.id,
            ):
                return render(
                    request,
                    'alta_funcional/create.html',
                    dict(
                        form=form,
                        alta=alta,
                        error_message='Ese diagnóstico funcional ya está cargado para esta alta.',
                    )
                )

            altaFuncionalRepo.create(
                id_alta=form.cleaned_data['id_alta'],
                id_diagnostico_funcional=diagnostico_funcional,
                observaciones=form.cleaned_data['observaciones'],
                id_usuario=form.cleaned_data['id_usuario'],
            )
            messages.success(request, 'Diagnóstico funcional agregado correctamente.')
            return redirect('paciente_rehab_detail', alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalList(View):

    def get(self, request, alta_id):
        alta = altaRepo.get_by_id(id=alta_id)
        altas_funcionales = altaFuncionalRepo.filter_all_by_alta_id(alta_id=alta.id)
        paciente = pacienteRepo.get_by_id(id=alta.id_paciente_rehabilitacion.id_paciente_area.id_paciente.id)

        return render(
            request,
            'alta_funcional/list.html',
            dict(
                altas_funcionales=altas_funcionales,
                alta=alta,
                paciente=paciente,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalUpdate(View):

    template_name = 'alta_funcional/update.html'

    def get(self, request, alta_funcional_id):
        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_funcional_id)
        alta = alta_funcional.id_alta

        form = AltaFuncionalCreateForm(
            instance=alta_funcional,
            initial={'id_usuario': alta_funcional.id_usuario or request.user, 'id_alta': alta},
        )

        return render(
            request,
            'alta_funcional/update.html',
            dict(
                form=form,
                alta=alta,
                alta_funcional=alta_funcional,
            )
        )

    def post(self, request, alta_funcional_id):
        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_funcional_id)
        alta = alta_funcional.id_alta

        form = AltaFuncionalCreateForm(request.POST, instance=alta_funcional)
        if form.is_valid():
            diagnostico_funcional = form.cleaned_data['id_diagnostico_funcional']
            if altaFuncionalRepo.exists_active_by_alta_and_diagnostico(
                alta_id=alta.id,
                diagnostico_funcional_id=diagnostico_funcional.id,
                exclude_alta_funcional_id=alta_funcional.id,
            ):
                return render(
                    request,
                    'alta_funcional/update.html',
                    dict(
                        form=form,
                        alta=alta,
                        alta_funcional=alta_funcional,
                        error_message='Ese diagnóstico funcional ya está cargado para esta alta.',
                    )
                )

            altaFuncionalRepo.update(
                alta_funcional=alta_funcional,
                id_diagnostico_funcional=diagnostico_funcional,
                observaciones=form.cleaned_data['observaciones'],
            )
            messages.success(request, 'Diagnóstico funcional actualizado correctamente.')
            return redirect('alta_funcional_list', alta_id=alta.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AltaFuncionalRemove(View):

    def get(self, request, alta_funcional_id):
        alta_funcional = altaFuncionalRepo.get_by_id(id=alta_funcional_id)
        alta_id = alta_funcional.id_alta.id
        altaFuncionalRepo.delete_by_activo(alta_funcional=alta_funcional)
        messages.success(request, 'Diagnóstico funcional quitado correctamente.')
        return redirect('alta_funcional_list', alta_id=alta_id)
