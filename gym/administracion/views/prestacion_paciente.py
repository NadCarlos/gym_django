from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PrestacionCreateForm,
    )

from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.prestacion import PrestacionRepository


prestacionPacienteRepo = PrestacionPacienteRepository()
pacienteRepo = PacienteRepository()
prestacionRepo = PrestacionRepository()


class NuevaPrestacionPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PrestacionCreateForm(initial = {'id_paciente': paciente.id})
        return render(
            request,
            'prestacion_paciente/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, id, *args, **kwargs):
        form = PrestacionCreateForm(request.POST)
        try:
            if form.is_valid():
                nueva_prestacion_paciente = prestacionPacienteRepo.create(
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_fin=form.cleaned_data['fecha_fin'],
                    prestacion=form.cleaned_data['id_prestacion'],
                    paciente=form.cleaned_data['id_paciente'],
                    obraSocial=form.cleaned_data['id_obra_social'],
                    )
                return redirect('paciente_detail', nueva_prestacion_paciente.id_paciente.id)
        except:
            return redirect('error')