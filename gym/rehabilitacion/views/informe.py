from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.decorators import requiere_areas

from rehabilitacion.forms import(
    InformeCreateForm,
)

from rehabilitacion.repositories.informe import InformeRepository
from administracion.repositories.paciente import PacienteRepository


informeRepo = InformeRepository()
pacienteRepo = PacienteRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformesList(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        informes = informeRepo.filter_by_paciente_id(paciente_id=id)
        return render(
            request,
            'informes/list.html',
            dict(
                paciente=paciente,
                informes=informes,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = InformeCreateForm(initial = {
            'id_paciente': paciente,
            }
        )
        return render(
            request,
            'informes/create.html',
            dict(
                paciente=paciente,
                form=form,
            )
        )

    def post(self, request, id):
        form = InformeCreateForm(request.POST)
        if form.is_valid():
            informeRepo.create(
                fecha=form.cleaned_data['fecha'],
                id_profesional=form.cleaned_data['id_profesional'],
                id_paciente=form.cleaned_data['id_paciente'],
                observaciones=form.cleaned_data['observaciones'],
            )
        return redirect('informes', id)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeDetail(View):

    def get(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        print(informe)
        return render(
            request,
            'informes/detail.html',
            dict(
                informe=informe,
            )
        )