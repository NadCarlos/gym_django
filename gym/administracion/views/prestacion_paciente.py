from datetime import date

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PrestacionCreateForm,
    PrestacionUpdateForm,
    )

from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.prestacion import PrestacionRepository
from administracion.repositories.agenda import AgendaRepository


prestacionPacienteRepo = PrestacionPacienteRepository()
pacienteRepo = PacienteRepository()
prestacionRepo = PrestacionRepository()
agendaRepo = AgendaRepository()


class NuevaPrestacionPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        paciente_id = paciente.id
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente_id)
        if prestacion_paciente == None:
            form = PrestacionCreateForm(initial = {'id_paciente': paciente.id})
            return render(
                request,
                'prestacion_paciente/create.html',
                dict(
                    form=form
                    )
                )
        else:
            return redirect('active_error')
        
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, id, *args, **kwargs):
        form = PrestacionCreateForm(request.POST)
        try:
            if form.is_valid():
                nueva_prestacion_paciente = prestacionPacienteRepo.create(
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    prestacion=form.cleaned_data['id_prestacion'],
                    paciente=form.cleaned_data['id_paciente'],
                    obraSocial=form.cleaned_data['id_obra_social'],
                    )
                return redirect('paciente_detail', nueva_prestacion_paciente.id_paciente.id)
        except:
            return redirect('error')
        

class ListPrestacionPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        paciente_id = paciente.id
        prestaciones_paciente = prestacionPacienteRepo.filter_by_id_paciente_all(id_paciente=paciente_id)
        return render(
            request,
            'prestacion_paciente/list.html',
            dict(
                paciente=paciente,
                prestaciones_paciente=prestaciones_paciente
            )
        )
    

class PrestacionPacienteUpdate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        prestacionPaciente = prestacionPacienteRepo.get_by_id(id=id)
        form = PrestacionUpdateForm(instance=prestacionPaciente)
        return render(
            request,
            'prestacion_paciente/update.html',
            dict(
                form=form,
                prestacionPaciente=prestacionPaciente,
            )
        )

    @method_decorator(login_required(login_url='login'))
    def post(self, request, id):
        form = PrestacionUpdateForm(request.POST)
        prestacionPaciente = prestacionPacienteRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                prestacionPacienteRepo.update(
                    prestacionPaciente=prestacionPaciente,
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_fin=form.cleaned_data['fecha_fin'],
                    id_prestacion=form.cleaned_data['id_prestacion'],
                    id_obra_social=form.cleaned_data['id_obra_social'],
                    )
                return redirect('list_prestacion_paciente', prestacionPaciente.id_paciente.id)
        except:
            return redirect('error')
    

class DeletePrestacionPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id, *args, **kwargs):
        prestacionPaciente = prestacionPacienteRepo.get_by_id(id=id)
        agendas = agendaRepo.filter_by_id_prestacion_paciente(id_prestacion_paciente=prestacionPaciente.id)
        today = date.today()
        if agendas != None:
            for agenda in agendas:
                agendaRepo.end_date(
                    agenda=agenda,
                    fecha_fin=today,
                )
                agendaRepo.delete_by_activo(agenda=agenda)

        prestacionPacienteRepo.end_date(
            prestacionPaciente=prestacionPaciente,
            fecha_fin=today,
        )
        prestacionPacienteRepo.delete_by_activo(prestacion_paciente=prestacionPaciente)
        return redirect('list_prestacion_paciente', prestacionPaciente.id_paciente.id)
    

class ActiveError(View):

    def get(self, request):
        return render(
            request,
            'prestacion_paciente/active_error.html',
        )