from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import PacientePlanForm

from administracion.repositories.paciente_plan import PacientePlanRepository
from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.agenda import AgendaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository


pacientePlanRepo = PacientePlanRepository()
pacienteRepo = PacienteRepository()
agendaRepo = AgendaRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientePlanesList(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        planes_paciente = pacientePlanRepo.filter_by_paciente(id=id)
        paciente_plan_exist = pacientePlanRepo.paciente_plan_exist(id_paciente=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        agenda_exist = agendaRepo.filter_by_id_paciente_exist(id_prestacion_paciente=prestacion.id)

        return render(
            request,
            'paciente_plan/list.html',
            dict(
                paciente=paciente,
                planes_paciente=planes_paciente,
                paciente_plan_exist=paciente_plan_exist,
                agenda_exist=agenda_exist,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientePlanCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PacientePlanForm(initial = {
            'id_usuario': request.user,
            'id_paciente': paciente.id,
            }
        )
        return render(
            request,
            'paciente_plan/create.html',
            dict(
                form=form
            )
        )

    def post(self, request, id):
        form = PacientePlanForm(request.POST)
        try:
            if form.is_valid():
                pacientePlanRepo.create(
                    id_plan=form.cleaned_data['id_plan'],
                    fecha=form.cleaned_data['fecha'],
                    id_paciente=form.cleaned_data['id_paciente'],
                    id_usuario=form.cleaned_data['id_usuario'],
                    )
                return redirect('paciente_plan_list', id)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientePlanDelete(View):

    def get(self, request, id):
        paciente_plan = pacientePlanRepo.get_by_id(id=id)
        pacientePlanRepo.delete_by_activo(paciente_plan=paciente_plan)
        return redirect ('paciente_plan_list', paciente_plan.id_paciente.id)