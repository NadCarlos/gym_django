from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.agenda import AgendaRepository

from administracion.forms import AgendaCreateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRepo = AgendaRepository()


class AgendaPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'agenda/agenda.html',
            dict(
                paciente=paciente,
            )
        )


class AgendaPacienteCreate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = AgendaCreateForm()
        return render(
            request,
            'agenda/create.html',
            dict(
                paciente=paciente,
                form=form,
            )
        )



class AgendaProfesional(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        return render(
            request,
            'agenda/agenda.html',
        )