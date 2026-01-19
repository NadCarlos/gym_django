import datetime
from datetime import time, date

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas


from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.tratamiento import TratamientoRepository
from administracion.repositories.profesional_area import ProfesionalAreaRepository
from administracion.repositories.paciente_area import PacienteAreaRepository

from rehabilitacion.forms import AgendaRehabCreateForm, AgendaRehabUpdateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRehabRepo = AgendaRehabRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
tratamientoRepo = TratamientoRepository()
profesionalAreaRepo = ProfesionalAreaRepository()
pacienteAreaRepo = PacienteAreaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaPacienteRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)
        agenda = agendaRehabRepo.filter_by_paciente_area(id_paciente_area=pacienteArea.id)
        return render(
            request,
            'agenda/agenda_paciente_rehab.html',
            dict(
                path=path,
                paciente=paciente,
                agenda=agenda,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaPacienteRehabCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        date = datetime.datetime.now()
        dateSTR = date.strftime("%d-%m-%Y")
        tratamientosActivos = tratamientoRepo.filter_by_activo()
        form = AgendaRehabCreateForm(
            initial = {
                'id_usuario': request.user,
                'fecha': date,
            }
        )
        return render(
            request,
            'agenda/rehab_create.html',
            dict(
                paciente=paciente,
                tratamientosActivos=tratamientosActivos,
                dateSTR=dateSTR,
                form=form,
            )
        )
    
    def post(self, request, id):
        form = AgendaRehabCreateForm(request.POST)
        if form.is_valid():
            paciente = pacienteRepo.get_by_id(id=id)
            pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)

            tratamiento_id = request.POST.get('id_tratamiento')
            tratamiento = tratamientoRepo.get_by_id(id=tratamiento_id)

            profesional = request.POST.get('profesional')
            profesional = profesionalRepo.filter_by_id(id=profesional)
            profesionalArea = profesionalAreaRepo.filter_by_profesional_id(id_profesional=profesional.id, id_area=2)

            hora_inicio=form.cleaned_data['hora_inicio'],
            hora_fin=form.cleaned_data['hora_fin'],
            # Convierte horas y minutos a minutos totales para ambos tiempos
            hora_inicio_total_minutos = hora_inicio[0].hour * 60 + hora_inicio[0].minute
            hora_fin_total_minutos = hora_fin[0].hour * 60 + hora_fin[0].minute
            if hora_fin_total_minutos <= hora_inicio_total_minutos:
                return redirect('error_hora')
            diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
            diferencia_horas = diferencia_minutos / 60

            observaciones=form.cleaned_data['observaciones']
            try:
                observaciones=observaciones.upper()
            except:
                pass
            
            agendaRehabRepo.create(
                id_usuario=form.cleaned_data['id_usuario'],
                fecha=form.cleaned_data['fecha'],
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                id_dia=form.cleaned_data['id_dia'],
                tiempo=diferencia_horas,
                id_tratamiento_rehab=tratamiento,
                id_paciente_area=pacienteArea,
                id_profesional_area=profesionalArea,
                observaciones=observaciones,
            )

            return redirect('agenda_paciente_rehab', paciente.id)
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaPacienteRehabUpdate(View):

    def get(self, request, id):
        agenda = agendaRehabRepo.get_by_id(id=id)
        paciente = agenda.id_paciente_area.id_paciente
        profesional_old = agenda.id_profesional_area.id_profesional
        tratamiento_old = agenda.id_tratamiento_rehab
        tratamientosActivos = tratamientoRepo.filter_by_activo()
        form = AgendaRehabUpdateForm(instance=agenda)
        return render(
            request,
            'agenda/rehab_update.html',
            dict(
                form=form,
                paciente=paciente,
                tratamientosActivos=tratamientosActivos,
                profesional_old=profesional_old,
                tratamiento_old=tratamiento_old,
            )
        )
    
    def post(self, request, id):
        agenda = agendaRehabRepo.get_by_id(id=id)
        form = AgendaRehabUpdateForm(request.POST)
        path = request.session.get('uid')
        if form.is_valid():
            tratamiento_id = request.POST.get('id_tratamiento')
            tratamiento = tratamientoRepo.filter_by_id(id=tratamiento_id)

            profesional = request.POST.get('profesional')
            profesional = profesionalRepo.filter_by_id(id=profesional)
            profesionalArea = profesionalAreaRepo.filter_by_profesional_id(id_profesional=profesional.id, id_area=2)

            hora_inicio=form.cleaned_data['hora_inicio'],
            hora_fin=form.cleaned_data['hora_fin'],
            # Convierte horas y minutos a minutos totales para ambos tiempos
            hora_inicio_total_minutos = hora_inicio[0].hour * 60 + hora_inicio[0].minute
            hora_fin_total_minutos = hora_fin[0].hour * 60 + hora_fin[0].minute
            if hora_fin_total_minutos <= hora_inicio_total_minutos:
                return redirect('error_hora')
            diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
            diferencia_horas = diferencia_minutos / 60

            observaciones=form.cleaned_data['observaciones']
            observaciones=observaciones.upper()
            
            agendaRehabRepo.update(
                agenda=agenda,
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                id_dia=form.cleaned_data['id_dia'],
                tiempo=diferencia_horas,
                id_tratamiento_rehab=tratamiento,
                id_profesional_area=profesionalArea,
                observaciones=observaciones,
            )

            return redirect( path )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaRehabDelete(View):

    def get(self, request, id, *args, **kwargs):
        path = request.session.get('uid')
        agenda = agendaRehabRepo.get_by_id(id=id)
        today = date.today()
        agendaRehabRepo.end_date(
            agenda=agenda,
            fecha_fin=today,
            )
        #No elimino, cambio el campo activo a False
        agendaRehabRepo.delete_by_activo(agenda=agenda)
        return redirect( path )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaProfesionalRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        profesional = profesionalRepo.get_by_id(id=id)
        profesionalArea = profesionalAreaRepo.filter_by_profesional_id(id_profesional=profesional.id, id_area=2)
        agenda = agendaRehabRepo.filter_by_id_profesional_area(id_profesional_area=profesionalArea.id)
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