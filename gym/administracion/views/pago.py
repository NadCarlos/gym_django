from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PagoForm,
)

from administracion.repositories.pago import PagoRepository
from administracion.repositories.detalle_pago import DetallePagoRepository
from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.cuota import CuotaRepository


pagoRepo = PagoRepository()
detallePagoRepo = DetallePagoRepository()
pacienteRepo = PacienteRepository()
cuotaRepo = CuotaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class PagoList(View):
     
    def get(self, request, id):
        cuota = cuotaRepo.get_by_id(id=id)
        detalles_pago = detallePagoRepo.filter_by_cuota_id(id_cuota=cuota.id)
        paciente = pacienteRepo.get_by_id(id=cuota.id_paciente_plan.id_paciente.id)
        return render(
            request,
            'pago/list.html',
            dict(
                cuota=cuota,
                detalles_pago=detalles_pago,
                paciente=paciente,
            )
        )
         

@method_decorator(login_required(login_url='login'), name='dispatch')
class PagoCreate(View):

    def get(self, request, id, id_c):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PagoForm(initial = {
            'id_usuario': request.user,
            'id_paciente': paciente,
            }
        )
        return render(
            request,
            'pago/create.html',
            dict(
                form=form
            )
        )
    
    def post(self, request, id, id_c):
        form = PagoForm(request.POST)
        cuota = cuotaRepo.get_by_id(id=id_c)
        if form.is_valid():
                pago = pagoRepo.create(
                    fecha=form.cleaned_data['fecha'],
                    id_tipo_pago=form.cleaned_data['id_tipo_pago'],
                    total=form.cleaned_data['total'],
                    id_paciente=form.cleaned_data['id_paciente'],
                    id_usuario=form.cleaned_data['id_usuario'],
                    )
                detalle_pago = detallePagoRepo.create(
                    id_pago=pago,
                    id_cuota=cuota,
                    importe=pago.total,
                )
                cuotaRepo.update_anulado(
                    cuota=cuota,
                    anulado=True,
                )
                return redirect('cuotas_list', False)


