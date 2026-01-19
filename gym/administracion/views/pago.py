from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from administracion.forms import (
    PagoForm,
)

from administracion.filters import DetallePagoFilter

from administracion.repositories.pago import PagoRepository
from administracion.repositories.detalle_pago import DetallePagoRepository
from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.cuota import CuotaRepository


pagoRepo = PagoRepository()
detallePagoRepo = DetallePagoRepository()
pacienteRepo = PacienteRepository()
cuotaRepo = CuotaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PagoList(View):
    template_name = 'pago/list.html'
    context_object_name = 'detalles_pago'
     
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        filterset = DetallePagoFilter(request.GET, detallePagoRepo.filter_by_paciente_id(id_paciente=id))

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', '-id_cuota')

        # Obtener el queryset filtrado
        detalles_pago = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            detalles_pago = filterset.qs.order_by(ordering)

        detalles_pago_count = detalles_pago.count()

        total = 0
        for detalle in detalles_pago:
            total += detalle.importe
        
        return render(
            request,
            self.template_name,
            dict(
                form=filterset.form,
                detalles_pago=detalles_pago,
                detalles_pago_count=detalles_pago_count,
                paciente=paciente,
                total=total,
            )
        )
         

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
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


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PagoDelete(View):
     
    def get(self, request, id):
        pago = pagoRepo.filter_by_id(id=id)
        detalle_pago = detallePagoRepo.filter_by_pago_id(id_pago=pago.id)
        pagoRepo.delete_by_activo(pago=pago)
        detallePagoRepo.delete_by_activo(detalle_pago=detalle_pago)

        return redirect('pago_list', pago.id_paciente.id)