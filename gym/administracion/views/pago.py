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
    

class PagoCreate(View):

    @method_decorator(login_required(login_url='login'))
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
    
    @method_decorator(login_required(login_url='login'))
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
                return redirect('cuotas_list')
