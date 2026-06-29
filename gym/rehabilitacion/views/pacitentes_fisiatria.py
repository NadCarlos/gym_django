from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from utils.decorators import requiere_areas

import json
import pandas as pd
import io
from datetime import datetime, date

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
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
#from administracion.repositories.agenda import AgendaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.paciente_plan import PacientePlanRepository
from administracion.repositories.cuota import CuotaRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from administracion.repositories.area import AreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.alta_etiologico import AltaEtiologicoRepository
from rehabilitacion.repositories.alta_funcional import AltaFuncionalRepository
from rehabilitacion.repositories.alta_tipo_discapacidad import AltaTipoDiscapacidadRepository

from rehabilitacion.repositories.estado_certificado import EstadoCertificadoRepository
from rehabilitacion.repositories.derivador import DerivadorRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository

estadoCertificadoRepo = EstadoCertificadoRepository()
derivadorRepo = DerivadorRepository()

pacienteRepo = PacienteRepository()
obraSocialRepo = ObraSocialRepository()
sexoRepo = SexoRepository()
prestacionRepo = PrestacionRepository()
localidadRepo = LocalidadRepository()
estadoCivilRepo = EstadoCivilRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
#agendaRepo = AgendaRepository()
pacientePlanRepo = PacientePlanRepository()
cuotaRepo = CuotaRepository()
pacienteAreaRepo = PacienteAreaRepository()
areaRepo = AreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
altaEtiologicoRepo = AltaEtiologicoRepository()
altaFuncionalRepo = AltaFuncionalRepository()
altaTipoDiscapacidadRepo = AltaTipoDiscapacidadRepository()
agendaRepo = AgendaRehabRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class PacientesFisiatriaList(View):
    template_name = 'pacientes_fisiatria/list.html'
    context_object_name = 'pacientes_fisiatria'

    def get(self, request, state):
        filterset = PacienteFilter(request.GET, pacienteRepo.filter_pacientes_area(state, id_area=3))

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        # Obtener el queryset filtrado
        pacientes = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            pacientes = filterset.qs.order_by(ordering)

        pacientes_count = pacientes.count()

        return render(
            request,
            self.template_name,
            dict(
                pacientes_count = pacientes_count,
                pacientes=pacientes,
                form=filterset.form,
                ordering=ordering,
                state=state,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class PacienteFisiatriaDetail(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'pacientes_fisiatria/detail.html',
            dict(
                paciente=paciente,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaCreate(View):

    def get(self, request):
        pacientes_dni_gym = pacienteRepo.dni_list_segun_area(id_area=1)
        pacientes_dni_rehab = pacienteRepo.dni_list_segun_area(id_area=2)
        pacientes_dni_area_actual = pacienteRepo.dni_list_segun_area(id_area=3)
        obra_social = obraSocialRepo.get_by_name(nombre="Particular")
        sexo = sexoRepo.get_by_name(nombre="Masculino")
        estado_civil = estadoCivilRepo.get_by_name(nombre="Soltero")
        localidad = localidadRepo.get_by_name(nombre="Rio Cuarto")
        form = PacienteCreateForm(initial = {
            'id_usuario': request.user,
            'id_obra_social': obra_social.id,
            'id_sexo': sexo.id,
            'id_estado_civil': estado_civil.id,
            'id_localidad': localidad.id,
            }
        )
        return render(
            request,
            'pacientes_fisiatria/create.html',
            dict(
                form=form,
                pacientes_dni_gym=json.dumps(pacientes_dni_gym),
                pacientes_dni_rehab=json.dumps(pacientes_dni_rehab),
                pacientes_dni_area_actual=json.dumps(pacientes_dni_area_actual),
            )
        )

    def post(self, request):
        form = PacienteCreateForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['numero_dni']
            dni=int(dni)
            pacienteExistente = pacienteRepo.filter_by_dni(numero_dni=dni, id_area=3)
            if pacienteExistente is None:
                area = areaRepo.get_by_id(id=3)
                nombre = form.cleaned_data['nombre']
                nombre = nombre.upper()
                apellido = form.cleaned_data['apellido']
                apellido = apellido.upper()
                paciente_nuevo = pacienteRepo.create(
                    id_usuario=form.cleaned_data['id_usuario'],
                    nombre=nombre,
                    apellido=apellido,
                    numero_dni=form.cleaned_data['numero_dni'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    id_obra_social=form.cleaned_data['id_obra_social'],
                    id_estado_civil=form.cleaned_data['id_estado_civil'],
                    id_sexo=form.cleaned_data['id_sexo'],
                    id_localidad=form.cleaned_data['id_localidad'],
                    direccion=form.cleaned_data['direccion'],
                    telefono=form.cleaned_data['telefono'],
                    celular=form.cleaned_data['celular'],
                    email=form.cleaned_data['email'],
                    observaciones=form.cleaned_data['observaciones'],
                    )
                paciente_area = pacienteAreaRepo.create(
                    id_paciente=paciente_nuevo,
                    id_area=area,
                    id_usuario=form.cleaned_data['id_usuario'],
                )
                return redirect('paciente_fisiatria_detail', paciente_nuevo.id)
            else:
                return redirect('error_paciente_existente')
        else:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaUpdate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PacienteUpdateForm(instance=paciente)
        return render(
            request,
            'pacientes_fisiatria/update.html',
            dict(
                form=form,
                paciente=paciente,
            )
        )

    def post(self, request, id):
        form = PacienteUpdateForm(request.POST)
        paciente = pacienteRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                dni = form.cleaned_data['numero_dni']
                dni=int(dni)
                pacienteExistente = pacienteRepo.filter_by_dni(numero_dni=dni, id_area=1)
                if pacienteExistente is None or pacienteExistente.id == paciente.id:
                    nombre = form.cleaned_data['nombre']
                    nombre = nombre.upper()
                    apellido = form.cleaned_data['apellido']
                    apellido = apellido.upper()
                    pacienteRepo.update(
                        paciente=paciente,
                        nombre=nombre,
                        apellido=apellido,
                        numero_dni=form.cleaned_data['numero_dni'],
                        direccion=form.cleaned_data['direccion'],
                        telefono=form.cleaned_data['telefono'],
                        celular=form.cleaned_data['celular'],
                        email=form.cleaned_data['email'],
                        observaciones=form.cleaned_data['observaciones'],
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        obra_social=form.cleaned_data['id_obra_social'],
                        estado_civil=form.cleaned_data['id_estado_civil'],
                        sexo=form.cleaned_data['id_sexo'],
                        localidad=form.cleaned_data['id_localidad'],
                        )
                    return redirect('paciente_fisiatria_detail', paciente.id)
                else:
                    return redirect('error_paciente_existente')
        except:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaCreateFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)
        user = request.user
        area = areaRepo.get_by_id(id=3)
        
        paciente_area = pacienteAreaRepo.create(
            id_paciente=paciente,
            id_area=area,
            id_usuario=user,
        )

        return redirect('paciente_rehab_detail', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaRedirectFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)

        return redirect('paciente_fisiatria_detail', paciente.id)
