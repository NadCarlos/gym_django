from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import date


from administracion.forms import PlanForm, PlanUpdateForm

from administracion.repositories.paciente_plan import PacientePlanRepository
from administracion.repositories.cuota import CuotaRepository


pacientePlanRepo = PacientePlanRepository()
cuotaRepo = CuotaRepository()


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
        return redirect('planes_list')

