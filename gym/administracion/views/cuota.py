from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import date

from administracion.filters import CuotaFilter

from administracion.repositories.paciente_plan import PacientePlanRepository
from administracion.repositories.cuota import CuotaRepository
from administracion.repositories.detalle_pago import DetallePagoRepository


pacientePlanRepo = PacientePlanRepository()
cuotaRepo = CuotaRepository()
detallePagoRepo = DetallePagoRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class GenerateCuotas(View):

    def get(self, request):
        planes_paciente = pacientePlanRepo.filter_by_activo()
        today = date.today()
        for plan_paciente in planes_paciente:
            if cuotaRepo.cuota_exist(id_paciente_plan=plan_paciente.id, year=today.year, month=today.month) == False:
                cuota = cuotaRepo.create(
                    imputado=today,
                    id_paciente_plan=plan_paciente,
                    valor=plan_paciente.id_plan.valor,
                )
            else:
                pass
        return redirect('cuotas_list', False)


@method_decorator(login_required(login_url='login'), name='dispatch')
class CuotasList(View):
    template_name = 'cuota/list.html'
    context_object_name = 'pacientes'

    def get(self, request, state):
        
        filterset = CuotaFilter(request.GET, queryset=cuotaRepo.filter_by_anulado(state=state))

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'id_paciente_plan__id_paciente__apellido')

        # Obtener el queryset filtrado
        cuotas = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            cuotas = filterset.qs.order_by(ordering)

        cuotas_count = cuotas.count()

        total = 0
        for cuota in cuotas:
            total += cuota.valor

        return render(
            request,
            self.template_name,
            dict(
                form=filterset.form,
                ordering=ordering,
                state=state,
                cuotas_count=cuotas_count,
                cuotas=cuotas,
                total=total,
            )
        )