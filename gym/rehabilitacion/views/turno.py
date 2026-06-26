from datetime import date, datetime, timedelta, time
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from utils.decorators import requiere_areas

from rehabilitacion.forms import TurnoCreateForm, TurnoUpdateForm

from rehabilitacion.repositories.turno import TurnoRepository
from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository


turnoRepo = TurnoRepository()
profesionalRepo = ProfesionalRepository()
pacienteAreaRepo = PacienteAreaRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TurnoList(View):

    def get(self, request):
        profesional_id = request.GET.get('profesional')
        fecha = self.get_fecha_referencia(request.GET.get('fecha'))
        lunes = fecha - timedelta(days=fecha.weekday())
        viernes = lunes + timedelta(days=4)
        profesionales = profesionalRepo.filter_profesional_area(id_area=2)
        turnos = []
        if profesional_id:
            turnos = list(turnoRepo.filter_by_profesional_and_rango_fecha(
                profesional_id=profesional_id,
                fecha_inicio=lunes,
                fecha_fin=viernes,
            ))

        nombres_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        hora_limite_tarde = time(14, 0)

        agenda_dias = []
        for index, nombre in enumerate(nombres_dias):
            fecha_dia = lunes + timedelta(days=index)
            turnos_dia = [turno for turno in turnos if turno.fecha == fecha_dia]
            agenda_dias.append({
                "nombre": nombre,
                "fecha": fecha_dia,
                "manana": [turno for turno in turnos_dia if turno.hora < hora_limite_tarde],
                "tarde": [turno for turno in turnos_dia if turno.hora >= hora_limite_tarde],
            })

        return render(
            request,
            'turnos/list.html',
            dict(
                profesionales=profesionales,
                profesional_id=profesional_id,
                fecha=fecha.isoformat(),
                semana_inicio=lunes,
                semana_fin=viernes,
                agenda_dias=agenda_dias,
                turnos=turnos,
            )
        )
    
    def get_fecha_referencia(self, fecha):
        if not fecha:
            return date.today()
        try:
            return datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return date.today()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoCreate(View):

    def get(self, request):
        form = TurnoCreateForm()
        return render(
            request,
            'turnos/create.html',
            dict(
                form=form,
            )
        )

    def post(self, request):
        form = TurnoCreateForm(request.POST)
        if form.is_valid():
            turnoRepo.create(
                paciente=form.cleaned_data['paciente_id'],
                profesional=form.cleaned_data['profesional_id'],
                tratamiento=form.cleaned_data['tratamiento_id'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
            )
            return redirect('turnos_rehab')

        return render(
            request,
            'turnos/create.html',
            dict(
                form=form,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoUpdate(View):

    def get(self, request, id):
        turno = turnoRepo.get_by_id(id=id)
        print(turno)
        form = TurnoUpdateForm(instance=turno)
        return render(
            request,
            'turnos/update.html',
            dict(
                form=form,
            )
        )

    def post(self, request, id):
        turno = turnoRepo.get_by_id(id=id)
        form = TurnoUpdateForm(request.POST)
        if form.is_valid():
            turnoRepo.update(
                turno=turno,
                profesional=form.cleaned_data['profesional_id'],
                tratamiento=form.cleaned_data['tratamiento_id'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
            )
            return redirect('turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoEstadoUpdate(View):

    def post(self, request, id):
        redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'turnos_rehab'
        turno = turnoRepo.get_by_id(id=id)
        if turno is None:
            return redirect(redirect_to)

        if turno.estado == turno.ESTADO_ANULADO:
            messages.error(request, 'El turno anulado no puede volver a editarse.')
            return redirect(redirect_to)

        accion = request.POST.get('accion')
        motivo_anulacion = request.POST.get('motivo_anulacion', '').strip()

        if accion == 'REALIZADO':
            turnoRepo.marcar_realizado(turno=turno)
        elif accion == 'ANULADO':
            if not motivo_anulacion:
                messages.error(request, 'El motivo de anulacion es obligatorio.')
                return redirect(redirect_to)
            turnoRepo.anular(
                turno=turno,
                motivo_anulacion=motivo_anulacion,
                usuario_anulacion=request.user,
            )

        return redirect(redirect_to)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoDelete(View):

    def get(self, request, id, *args, **kwargs):
        turno = turnoRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        turnoRepo.delete_by_activo(turno=turno)
        return redirect(request.META.get('HTTP_REFERER') or 'turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TurnoPacienteDetailRedirect(View):

    def get(self, request, id):
        prioridades = [
            (2, 'paciente_rehab_detail'),
            (3, 'paciente_fisiatria_detail'),
            (1, 'paciente_detail'),
        ]

        for area_id, url_name in prioridades:
            if pacienteAreaRepo.paciente_area_exist(id=id, area_id=area_id):
                return redirect(url_name, id)

        messages.error(request, 'No se encontro el paciente en Rehabilitacion, Fisiatria ni Gimnasio.')
        return redirect(request.META.get('HTTP_REFERER') or 'turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TratamientosPorProfesionalRehabView(View):

    def get(self, request, profesional_id):
        tratamientos_profesional = tratamientoProfesionalRepo.tratamientos_profesional_turnos(profesional_id=profesional_id)

        data = [
            {
                "id": item.id_tratamiento.id,
                "nombre": item.id_tratamiento.nombre,
            }
            for item in tratamientos_profesional
        ]
        return JsonResponse(data, safe=False)
