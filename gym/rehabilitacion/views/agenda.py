import pandas as pd
import io
import datetime
from datetime import time, date

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository

from administracion.forms import AgendaCreateForm, AgendaUpdateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRehabRepo = AgendaRehabRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPacienteRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        agenda = agendaRehabRepo.filter_by_id_paciente(id_prestacion_paciente=prestacion.id)
        return render(
            request,
            'agenda/agenda_paciente.html',
            dict(
                path=path,
                paciente=paciente,
                agenda=agenda,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaProfesionalRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        profesional = profesionalRepo.get_by_id(id=id)
        agenda = agendaRehabRepo.filter_by_activo(state=True)
        return render(
            request,
            'agenda/agenda_profesional_rehab.html',
            dict(
                path=path,
                profesional=profesional,
                agenda=agenda,
                hora_limite_tarde=time(14, 0),
            )
        )