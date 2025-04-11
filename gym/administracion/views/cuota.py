from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import PlanForm, PlanUpdateForm

from administracion.repositories.paciente_plan import PacientePlanRepository


pacientePlanRepo = PacientePlanRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class GenerateCuotas(View):

    def get(self, request):
        planes_paciente = pacientePlanRepo.filter_by_activo()
        for plan_paciente in planes_paciente:
            print(plan_paciente)

        return redirect('planes_list')