from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.agenda import AgendaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository

from administracion.forms import AgendaCreateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRepo = AgendaRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPaciente(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        agenda = agendaRepo.filter_by_id_paciente(id_prestacion_paciente=prestacion.id)
        return render(
            request,
            'agenda/agenda_paciente.html',
            dict(
                paciente=paciente,
                agenda=agenda,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPacienteCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        profesionales = profesionalRepo.filter_by_activo()
        tratamientosActivos = tratamientoProfesionalRepo.filter_by_activo()
        form = AgendaCreateForm(
            initial = {
                'id_usuario': request.user,
            }
        )
        return render(
            request,
            'agenda/create.html',
            dict(
                paciente=paciente,
                profesionales=profesionales,
                tratamientosActivos=tratamientosActivos,
                form=form,
            )
        )
    
    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        form = AgendaCreateForm(request.POST)
        if form.is_valid():
            hora_inicio=form.cleaned_data['hora_inicio'],
            hora_fin=form.cleaned_data['hora_fin'],

            # Convierte horas y minutos a minutos totales para ambos tiempos
            hora_inicio_total_minutos = hora_inicio[0].hour * 60 + hora_inicio[0].minute
            hora_fin_total_minutos = hora_fin[0].hour * 60 + hora_fin[0].minute
            if hora_fin_total_minutos <= hora_fin_total_minutos:
                return redirect('error_hora')
            diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
            
            agendaRepo.create(
                id_usuario=form.cleaned_data['id_usuario'],
                fecha=form.cleaned_data['fecha'],
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                id_prestacion_paciente=prestacion,
                id_profesional_tratamiento=form.cleaned_data['id_profesional_tratamiento'],
                id_dia=form.cleaned_data['id_dia'],
                tiempo=diferencia_minutos,
            )

            return redirect('agenda_paciente', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaProfesional(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        agenda = agendaRepo.get_all()
        return render(
            request,
            'agenda/agenda_profesional.html',
            dict(
                profesional=profesional,
                agenda=agenda,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ErrorPrestacionFaltante(View):

    def get(self, request):
        return render(
            request,
            'agenda/error_prestacion_paciente.html',
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ErrorHora(View):

    def get(self, request):
        return render(
            request,
            'agenda/error_hora.html',
        )