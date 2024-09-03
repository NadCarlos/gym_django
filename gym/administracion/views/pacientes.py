from typing import Any
from django.views import View
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.filters import PacienteFilter

from administracion.forms import (
    PacienteCreateForm,
    PacienteUpdateForm,
    )

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.obra_social import ObraSocialRepository
from administracion.repositories.sexo import SexoRepository
from administracion.repositories.prestacion import PrestacionRepository
from administracion.repositories.localidad import LocalidadRepository
from administracion.repositories.estado_civil import EstadoCivilRepository


pacienteRepo = PacienteRepository()
obraSocialRepo = ObraSocialRepository()
sexoRepo = SexoRepository()
prestacionRepo = PrestacionRepository()
localidadRepo = LocalidadRepository()
estadoCivilRepo = EstadoCivilRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientesList(ListView):
    queryset = pacienteRepo.filter_by_activo()
    template_name = 'pacientes/list.html'
    context_object_name = 'pacientes'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PacienteFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context


class PacienteDetail(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'pacientes/detail.html',
            dict(
                paciente=paciente,
            )
        )

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacienteCreate(View):

    def get(self, request):
        obra_social = obraSocialRepo.get_by_name(nombre="Particular")
        sexo = sexoRepo.get_by_name(nombre="Masculino")
        estado_civil = estadoCivilRepo.get_by_name(nombre="Soltero")
        localidad = localidadRepo.get_by_name(nombre="Rio Cuarto")
        form = PacienteCreateForm(initial = {
            'id_usuario': request.user,
            'id_obra_social': obra_social.id,
            'id_sexo': sexo.id,
            'id_estado_civil': estado_civil.id,
            'id_localidad': localidad.id
            }
        )
        return render(
            request,
            'pacientes/create.html',
            dict(
                form=form
            )
        )

    def post(self, request):
        form = PacienteCreateForm(request.POST)
        print(form)
        if form.is_valid():
                paciente_nuevo = pacienteRepo.create(
                    nombre=form.cleaned_data['nombre'],
                    apellido=form.cleaned_data['apellido'],
                    numero_dni=form.cleaned_data['numero_dni'],
                    direccion=form.cleaned_data['direccion'],
                    telefono=form.cleaned_data['telefono'],
                    celular=form.cleaned_data['celular'],
                    observaciones=form.cleaned_data['observaciones'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    obraSocial=form.cleaned_data['id_obra_social'],
                    estadoCivil=form.cleaned_data['id_estado_civil'],
                    sexo=form.cleaned_data['id_sexo'],
                    localidad=form.cleaned_data['id_localidad'],
                    usuario=form.cleaned_data['id_usuario'],
                    )
                return redirect('paciente_detail', paciente_nuevo.id)


class PacienteUpdate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PacienteUpdateForm(instance=paciente)
        return render(
            request,
            'pacientes/update.html',
            dict(
                form=form,
                paciente=paciente,
            )
        )

    @method_decorator(login_required(login_url='login'))
    def post(self, request, id):
        form = PacienteUpdateForm(request.POST)
        paciente = pacienteRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                pacienteRepo.update(
                    paciente=paciente,
                    nombre=form.cleaned_data['nombre'],
                    apellido=form.cleaned_data['apellido'],
                    numero_dni=form.cleaned_data['numero_dni'],
                    direccion=form.cleaned_data['direccion'],
                    telefono=form.cleaned_data['telefono'],
                    celular=form.cleaned_data['celular'],
                    observaciones=form.cleaned_data['observaciones'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    obra_social=form.cleaned_data['id_obra_social'],
                    estado_civil=form.cleaned_data['id_estado_civil'],
                    sexo=form.cleaned_data['id_sexo'],
                    localidad=form.cleaned_data['id_localidad'],
                    )
                return redirect('paciente_detail', paciente.id)
        except:
            return redirect('error')


class PacienteDelete(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        pacienteRepo.delete_by_activo(paciente=paciente)
        return redirect('pacientes_list')