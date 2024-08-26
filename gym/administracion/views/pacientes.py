from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PacienteCreateForm,
    )

from administracion.repositories.paciente import PacienteRepository


pacienteRepo = PacienteRepository()


class PacientesList(View):

    @method_decorator(permission_required(perm='gym.pacientes_list', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        pacientes = pacienteRepo.filter_by_activo()
        return render(
            request,
            'pacientes/list.html',
            dict(
                pacientes=pacientes
            )
        )


class PacienteDetail(View):

    @method_decorator(permission_required(perm='gym.paciente_detail', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'pacientes/detail.html',
            dict(
                paciente=paciente,
            )
        )


class PacienteCreate(View):

    @method_decorator(permission_required(perm='gym.paciente_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        form = PacienteCreateForm(initial = {'id_usuario': request.user})
        return render(
            request,
            'pacientes/create.html',
            dict(
                form=form
            )
        )

    @method_decorator(permission_required(perm='gym.paciente_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def post(self, request):
        form = PacienteCreateForm(request.POST)
        try:
            if form.is_valid():
                paciente_nuevo = pacienteRepo.create(
                    nombre=form.cleaned_data['nombre'],
                    apellido=form.cleaned_data['apellido'],
                    numero_dni=form.cleaned_data['numero_dni'],
                    direccion=form.cleaned_data['direccion'],
                    telefono=form.cleaned_data['telefono'],
                    celular=form.cleaned_data['celular'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    obraSocial=form.cleaned_data['id_obra_social'],
                    estadoCivil=form.cleaned_data['id_estado_civil'],
                    sexo=form.cleaned_data['id_sexo'],
                    localidad=form.cleaned_data['id_localidad'],
                    usuario=form.cleaned_data['id_usuario'],
                    )
                return redirect('paciente_detail', paciente_nuevo.id)
        except:
            return redirect('error')


class PacienteDelete(View):

    @method_decorator(permission_required(perm='gym.paciente_delete', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        pacienteRepo.delete_by_activo(paciente=paciente)
        return redirect('pacientes_list')
    