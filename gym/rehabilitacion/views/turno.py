from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from utils.decorators import requiere_areas
from administracion.models import ProfesionalTratamiento
from administracion.repositories.profesional import ProfesionalRepository
from rehabilitacion.forms import TurnoCreateForm
from rehabilitacion.repositories.turno import TurnoRepository


turnoRepo = TurnoRepository()
profesionalRepo = ProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoList(View):

    def get(self, request):
        profesional_id = request.GET.get('profesional')
        fecha = request.GET.get('fecha')
        profesionales = profesionalRepo.get_all()
        turnos = turnoRepo.filter_by_profesional_and_fecha(
            profesional_id=profesional_id,
            fecha=fecha,
        )

        return render(
            request,
            'turnos/list.html',
            dict(
                profesionales=profesionales,
                profesional_id=profesional_id,
                fecha=fecha,
                turnos=turnos,
            )
        )


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
class TratamientosPorProfesionalRehabView(View):

    def get(self, request, profesional_id):
        tratamientos_profesional = ProfesionalTratamiento.objects.filter(
            id_profesional_id=profesional_id,
            activo=True,
            id_tratamiento__activo=True,
        ).select_related('id_tratamiento').order_by('id_tratamiento__nombre')

        data = [
            {
                "id": item.id_tratamiento.id,
                "nombre": item.id_tratamiento.nombre,
            }
            for item in tratamientos_profesional
        ]
        return JsonResponse(data, safe=False)
