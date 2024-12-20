from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
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

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente(id_paciente=paciente.id)
        try:
            asistencias = asistenciaRepo.get_all_by_id(id_prestacion_paciente=prestacion_paciente.id)
            return render(
                request,
                'asistencia/list.html',
                dict(
                    paciente=paciente,
                    prestacion_paciente=prestacion_paciente,
                    asistencias=asistencias,
                )
            )
        except:
            return redirect('error_no_prestacion', paciente.id)

class NuevaAsistenciaPaciente(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion_paciente = prestacionPacienteRepo.filter_by_id_paciente(id_paciente=paciente.id)
        try:
            form = AsistenciaCreateForm(initial = {'id_prestacion_paciente': prestacion_paciente.id})
            return render(
                request,
                'asistencia/create.html',
                dict(
                    paciente=paciente,
                    form=form
                )
            )
        except:
            return redirect('error_no_prestacion', paciente.id)
    
    @method_decorator(login_required(login_url='login'))
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

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = AsistenciaPublicCreateForm()
        return render(
            request,
            'asistencia/check_in.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(login_required(login_url='login'))
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

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        try:
            if paciente.activo == False:
                return redirect('check_in_error')
            else:
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
        except:
            return redirect('check_in_not_found')
    
    @method_decorator(login_required(login_url='login'))
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

    @method_decorator(login_required(login_url='login'))
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

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        return render(
            request,
            'asistencia/check_in_error.html'
        )
    
class CheckInNotFound(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        return render(
            request,
            'asistencia/check_in_not_found.html'
        )
    

class PrestacionNotFound(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'asistencia/error_no_prestacion.html',
            dict(
                paciente=paciente,
            )
        )
    
    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'pacientes/detail.html',
            dict(
                paciente=paciente,
            )
        )