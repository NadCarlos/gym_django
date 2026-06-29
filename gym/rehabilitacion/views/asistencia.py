from datetime import date, datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from rehabilitacion.forms import (
    AsistenciaRehabPublicCreateForm,
    )

from administracion.repositories.paciente import PacienteRepository
from rehabilitacion.repositories.asistencia import AsistenciaRehabRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository

pacienteRepo = PacienteRepository()
asistenciaRepo = AsistenciaRehabRepository()
agendaRepo = AgendaRehabRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabManual(View):

    def post(self, request, id, fecha):
        paciente = pacienteRepo.get_by_id(id=id)
        agenda = agendaRepo.filter_by_id_paciente(id_paciente=paciente.id)

        if fecha:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        else:
            fecha = date.today()

        id_dia = fecha.weekday() + 1

        turnos_del_dia = [
            turno for turno in agenda
            if turno.id_dia.id == id_dia
        ]

        tiene_asistencia = asistenciaRepo.filter_by_date(id_paciente=paciente.id,fecha=fecha)

        if len(tiene_asistencia) == 0:
            now = datetime.now()
            current_hour = now.hour
            for turno in turnos_del_dia:
                asistenciaRepo.create(
                    id_agenda_rehab=turno,
                    fecha=fecha,
                    hora=current_hour,
                )

            return redirect('asistencias_rehab_list')
        else:
            return redirect('check_in_error_asistencia_registrada_manual')


@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehab(View):

    def get(self, request):
        form = AsistenciaRehabPublicCreateForm()
        return render(
            request,
            'asistencia_rehab/check_in.html',
            dict(
                form=form
            )
        )

    def post(self, request):
        form = AsistenciaRehabPublicCreateForm(request.POST or None)
        if form.is_valid():
                dni = form.cleaned_data['numero_dni']
                dni=int(dni)
                paciente = pacienteRepo.filter_by_dni(numero_dni=dni, id_area=2)
                if paciente == None:
                    return redirect('check_in_error_dni')
                
                agenda = agendaRepo.filter_by_id_paciente(id_paciente=paciente.id)
                if len(agenda) == 0:
                    return redirect('check_in_error_agenda_activa')
                
                dias = [1,2,3,4,5]
                today = date.today()
                dia = dias[today.weekday()]
                turnosDelDia = []
                for turno in agenda:
                    if turno.id_dia.id == dia:
                        turnosDelDia.append(turno)

                if len(turnosDelDia) == 0:
                    dia = dia + 1
                    while len(turnosDelDia) == 0:
                        for turno in agenda:
                            if turno.id_dia.id == dia:
                                turnosDelDia.append(turno)
                        dia = dia + 1
                        if dia >= 6:
                            dia = 1
                    turnoSiguiente = turnosDelDia[0]
                    return redirect('check_in_error_dia_incorrecto', turnoSiguiente.id)
                
                tiene_asistencia_del_dia = asistenciaRepo.filter_by_date(id_paciente=paciente.id, fecha=today)
                if len(tiene_asistencia_del_dia) == 0:
                    now = datetime.now()
                    current_day = now.day
                    current_hour = now.hour
                    for turno in turnosDelDia:
                        asistenciaRepo.create(
                            id_agenda_rehab=turno,
                            fecha=current_day,
                            hora=current_hour,
                        )
                    return render(
                        request,
                        'asistencia_rehab/check_in_success.html',
                        dict(
                            paciente=paciente,
                            date=today,
                        )
                    )
                else:
                    return redirect('check_in_error_asistencia_registrada')

        

@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabErrorDni(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_dni.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabErrorAgendaActiva(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_agenda_activa.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabErrorAsistenciaRegistrada(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_asistencia_registrada.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabErrorAsistenciaRegistradaManual(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_asistencia_registrada_manual.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class CheckInRehabErrorDiaIncorrecto(View):

    def get(self, request, id):
        agenda = agendaRepo.filter_by_id(id=id)
        return render(
            request,
            'asistencia_rehab/check_in_error_dia_incorrecto.html',
            dict(
                agenda=agenda
            )
        )