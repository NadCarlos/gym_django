from datetime import date

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
                    return HttpResponse("HAPPY HAPPY HAPPY")
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