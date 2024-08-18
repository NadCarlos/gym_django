from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

import datetime

from entrada.forms import (
    AsistenciaCreateForm,
    AsistenciaPublicCreateForm,
    )


from entrada.repositories.asistencia import AsistenciaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.paciente import PacienteRepository

pacienteRepo = PacienteRepository()
asistenciaRepo = AsistenciaRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()


class AsistenciaPacienteList(View):

    @method_decorator(permission_required(perm='gym.historial_aistencias_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente(id_paciente=paciente.id)
        asistencias = asistenciaRepo.get_all_by_id(id_prestacion_paciente=prestacion_paciente.id)
        return render(
            request,
            'asistencia/list.html',
            dict(
                asistencias=asistencias
            )
        )


class NuevaAsistenciaPaciente(View):

    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente(id_paciente=paciente.id)
        form = AsistenciaCreateForm(initial = {'id_prestacion_paciente': prestacion_paciente.id})
        return render(
            request,
            'asistencia/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def post(self, request, id, *args, **kwargs):
        form = AsistenciaCreateForm(request.POST)
        try:
            if form.is_valid():
                nueva_asistencia = asistenciaRepo.create(
                    prestacionPaciente=form.cleaned_data['id_prestacion_paciente'],
                    )
                return redirect('paciente_detail', nueva_asistencia.id_prestacion_paciente.id_paciente.id)
        except:
            return redirect('error')
        

class CheckIn(View):

    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        form = AsistenciaPublicCreateForm()
        return render(
            request,
            'asistencia/check_in.html',
            dict(
                form=form
            )
        )
    
    def post(self, request):
        form = AsistenciaPublicCreateForm(request.POST or None)
        try: 
            if request.POST and form.is_valid():
                dni = form.cleaned_data['numero_dni']
                dni=int(dni)
                paciente = pacienteRepo.get_by_dni(numero_dni=dni)
                return redirect ('check_in_confirm', paciente.id)
        except:
            return redirect('check_in_error')


class CheckInConfirm(View):

    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente(id_paciente=paciente.id)
        form = AsistenciaCreateForm(initial = {'id_prestacion_paciente': prestacion_paciente.id})
        return render(
            request,
            'asistencia/check_in_confirm.html',
            dict(
                form=form,
                paciente=paciente,
            )
        )
    
    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def post(self, request, id, *args, **kwargs):
        form = AsistenciaCreateForm(request.POST)
        paciente = pacienteRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nueva_asistencia = asistenciaRepo.create(
                    prestacionPaciente=form.cleaned_data['id_prestacion_paciente'],
                    )
                return redirect('check_in_success', paciente.id)
        except:
            return redirect('check_in_error')
        

class CheckInSuccess(View):

    @method_decorator(permission_required(perm='gym.nueva_asistencia_paciente', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request, id, *args, **kwargs):
        date = datetime.datetime.now()
        date = date.strftime("Fecha : %w-%m-%Y Hora: %I:%M")
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'asistencia/check_in_success.html',
            dict(
                paciente=paciente,
                date=date,
            )
        )
    

class CheckInError(View):

    def get(self, request):
        return render(
            request,
            'asistencia/check_in_error.html'
        )
    