from datetime import date, datetime

from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from utils.decorators import requiere_areas

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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class CheckInRehabManual(View):

    def post(self, request, id, fecha):
        paciente = pacienteRepo.get_by_id(id=id)
        agenda = agendaRepo.filter_by_id_paciente(id_paciente=paciente.id)

        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        id_dia = fecha.weekday() + 1

        turnos_del_dia = [
            turno for turno in agenda
            if turno.id_dia.id == id_dia
        ]

        asistencias_cargadas = set(
            asistenciaRepo
            .filter_by_date(id_paciente=paciente.id, fecha=fecha)
            .values_list("id_agenda_rehab_id", flat=True)
        )

        turnos_pendientes = [
            turno for turno in turnos_del_dia
            if turno.id not in asistencias_cargadas
        ]

        if len(turnos_pendientes) > 0:
            now = datetime.now()
            hora = now.time().replace(microsecond=0)
            for turno in turnos_pendientes:
                asistenciaRepo.create_manual(
                    id_agenda_rehab=turno,
                    fecha=fecha,
                    hora=hora,
                )

            return redirect(f"{reverse('asistencias_rehab_list')}?fecha={fecha}")
        else:
            return redirect('check_in_error_asistencia_registrada_manual')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class CheckInRehabAgendaManual(View):

    def post(self, request, id):
        agenda = agendaRepo.get_by_id(id=id)
        if agenda is None:
            messages.error(request, "No se encontró el turno de agenda.")
            return redirect(request.META.get("HTTP_REFERER", "inicio_rehab"))

        today = date.today()
        id_dia = today.weekday() + 1
        redirect_url = reverse(
            "agenda_profesional_rehab",
            args=[agenda.id_profesional_area.id_profesional_id],
        )

        if agenda.id_dia_id != id_dia:
            messages.error(request, "La asistencia solo se puede cargar para turnos del día de hoy.")
            return redirect(redirect_url)

        tiene_asistencia = asistenciaRepo.filter_by_agenda_date(
            id_agenda_rehab=agenda.id,
            fecha=today,
        )
        if tiene_asistencia.exists():
            messages.warning(request, "La asistencia para este turno ya está cargada.")
            return redirect(redirect_url)

        now = datetime.now()
        hora = now.time().replace(microsecond=0)
        asistenciaRepo.create_manual(
            id_agenda_rehab=agenda,
            fecha=today,
            hora=hora,
        )
        messages.success(request, "Asistencia cargada correctamente.")
        return redirect(redirect_url)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("IngresoRehab"), name="dispatch")
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
                hora = now.time().replace(microsecond=0)
                for turno in turnosDelDia:
                    asistenciaRepo.create(
                        id_agenda_rehab=turno,
                        fecha=today,
                        hora=hora,
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
@method_decorator(requiere_areas("IngresoRehab"), name="dispatch")
class CheckInRehabErrorDni(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_dni.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("IngresoRehab"), name="dispatch")
class CheckInRehabErrorAgendaActiva(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_agenda_activa.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("IngresoRehab"), name="dispatch")
class CheckInRehabErrorAsistenciaRegistrada(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_asistencia_registrada.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class CheckInRehabErrorAsistenciaRegistradaManual(View):

    def get(self, request):
        return render(
            request,
            'asistencia_rehab/check_in_error_asistencia_registrada_manual.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("IngresoRehab"), name="dispatch")
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
