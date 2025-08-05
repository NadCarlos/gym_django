from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

import json

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
from administracion.repositories.agenda import AgendaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.paciente_plan import PacientePlanRepository
from administracion.repositories.cuota import CuotaRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from administracion.repositories.area import AreaRepository


from administracion.models import Paciente


pacienteRepo = PacienteRepository()
obraSocialRepo = ObraSocialRepository()
sexoRepo = SexoRepository()
prestacionRepo = PrestacionRepository()
localidadRepo = LocalidadRepository()
estadoCivilRepo = EstadoCivilRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
agendaRepo = AgendaRepository()
pacientePlanRepo = PacientePlanRepository()
cuotaRepo = CuotaRepository()
pacienteAreaRepo = PacienteAreaRepository()
areaRepo = AreaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientesRehabList(View):
    template_name = 'pacientes_rehab/list.html'
    context_object_name = 'pacientes_rehab'

    def get(self, request, state):
        filterset = PacienteFilter(request.GET, pacienteRepo.filter_pacientes_area(state, id_area=2))

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
class PacienteRehabDetail(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'pacientes_rehab/detail.html',
            dict(
                paciente=paciente,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacienteRehabCreate(View):

    def get(self, request):
        pacientes_dni = pacienteRepo.dni_list_segun_area(state=True, id_area=1)
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
            'pacientes_rehab/create.html',
            dict(
                form=form,
                pacientes_dni=json.dumps(pacientes_dni),
            )
        )

    def post(self, request):
        form = PacienteCreateForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['numero_dni']
            dni=int(dni)
            pacienteExistente = pacienteRepo.filter_by_dni(numero_dni=dni, id_area=2)
            if pacienteExistente is None:
                area = areaRepo.get_by_id(id=2)
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
                    observaciones=form.cleaned_data['observaciones'],
                    )
                paciente_area = pacienteAreaRepo.create(
                    id_paciente=paciente_nuevo,
                    id_area=area,
                    id_usuario=form.cleaned_data['id_usuario'],
                )
                return redirect('paciente_detail', paciente_nuevo.id)
            else:
                return redirect('error_paciente_existente')
        else:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacienteRehabCreateFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)
        user = request.user
        area = areaRepo.get_by_id(id=2)
        
        paciente_area = pacienteAreaRepo.create(
            id_paciente=paciente,
            id_area=area,
            id_usuario=user,
        )

        return redirect('paciente_rehab_detail', paciente.id)