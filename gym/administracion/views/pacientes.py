import pandas as pd
import io
import json

from datetime import date

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import OperationalError
from django.shortcuts import render, redirect, HttpResponse
from utils.decorators import requiere_areas

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
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PacientesList(View):
    template_name = 'pacientes/list.html'
    context_object_name = 'pacientes'

    def get(self, request, state):
        filterset = PacienteFilter(request.GET, pacienteRepo.filter_pacientes_area(state, id_area=1))
        """pacientesFinished = []
        for paciente in pacientes:
            for prestacion in prestaciones:
                if paciente.id == prestacion.id_paciente.id and prestacion.activo == True:
                    tiene_prestacion_activa = 'Prestacion Activa'
                    paciente.__dict__['tiene_prestacion_activa'] = tiene_prestacion_activa
                    break
            else:
                tiene_prestacion_activa = 'Sin Prestacion Activa'
                paciente.__dict__['tiene_prestacion_activa'] = tiene_prestacion_activa
            pacientesFinished.append(paciente)"""
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
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion", "Profesional"), name="dispatch")
class PacientesToCsv(View):

    def get(self, request, state, area):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        if area == 1:
            response['Content-Disposition'] = 'attachment; filename=pacientes_gimnasio.xlsx'
        else:
            response['Content-Disposition'] = 'attachment; filename=pacientes_rehabilitacion.xlsx'
            
        apellido = request.GET.get('apellido')
        id_obra_social = request.GET.get('id_obra_social')
        id_estado_civil = request.GET.get('id_estado_civil')
        id_sexo = request.GET.get('id_sexo')

        pacientes = pacienteRepo.filter_pacientes_area_for_export(state, id_area=area)

        if apellido:
            pacientes = pacientes.filter(apellido__icontains=apellido)

        if id_obra_social:
            pacientes = pacientes.filter(id_obra_social=id_obra_social)

        if id_estado_civil:
            pacientes = pacientes.filter(id_estado_civil=id_estado_civil)

        if id_sexo:
            pacientes = pacientes.filter(id_sexo=id_sexo)

        data = []
        for paciente in pacientes:
            tiene_prestacion_activa = (
                'Prestacion Activa'
                if paciente.tiene_prestacion_activa
                else 'Sin Prestacion Activa'
            )

            row = [
                paciente.nombre,
                paciente.apellido,
                paciente.numero_dni,
                paciente.direccion,
                paciente.telefono,
                paciente.celular,
                paciente.fecha_nacimiento,
                paciente.observaciones,
                paciente.activo,
                paciente.id_obra_social.nombre if paciente.id_obra_social else '',
                paciente.id_estado_civil.nombre if paciente.id_estado_civil else '',
                paciente.id_localidad.nombre if paciente.id_localidad else '',
                paciente.id_sexo.nombre if paciente.id_sexo else '',
                tiene_prestacion_activa,
            ]
            if area == 2:
                row.append(paciente.ultima_situacion or "")
            data.append(row)

        columns = [
            'Nombre',
            'Apellido',
            'Dni',
            'Direccion',
            'Telefono',
            'Celular',
            'Fecha de nacimiento',
            'observaciones',
            'activo',
            'obra social',
            'estado civil',
            'localidad',
            'sexo',
            'Prestacion Activa',
        ]
        if area == 2:
            columns.append('Ultima Situacion')

        df = pd.DataFrame(data, columns=columns)

        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Pacientes', index=False)

        response.write(output.getvalue())

        return response


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PacienteDetail(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=1, id_paciente=paciente.id)
        return render(
            request,
            'pacientes/detail.html',
            dict(
                paciente=paciente,
                pacienteArea=pacienteArea,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PacienteCreate(View):

    def get(self, request):
        pacientes_dni_rehab = pacienteRepo.dni_list_segun_area(id_area=2)
        pacientes_dni_fisio = pacienteRepo.dni_list_segun_area(id_area=3)
        pacientes_dni_area_actual = pacienteRepo.dni_list_segun_area(id_area=1)
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
                form=form,
                pacientes_dni_rehab=json.dumps(pacientes_dni_rehab),
                pacientes_dni_fisio=json.dumps(pacientes_dni_fisio),
                pacientes_dni_area_actual=json.dumps(pacientes_dni_area_actual),
            )
        )

    def post(self, request):
        form = PacienteCreateForm(request.POST)
        if not form.is_valid():
            return redirect('error')

        area = areaRepo.get_by_id(id=1)
        paciente, area_created = pacienteRepo.create_in_area(
            id_area=area,
            id_usuario=request.user,
            nombre=form.cleaned_data['nombre'].upper(),
            apellido=form.cleaned_data['apellido'].upper(),
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
        if not area_created:
            return redirect('error_paciente_existente')
        return redirect('paciente_detail', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio"), name="dispatch")
class PacienteUpdate(View):

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
                    return redirect('paciente_detail', paciente.id)
                else:
                    return redirect('error_paciente_existente')
        except OperationalError:
            raise
        except Exception:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteDelete(View):
    http_method_names = ["post"]

    def post(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacionPaciente = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacionPaciente != None:
            today = date.today()
            agendaRepo.deactivate_for_patient_service(
                id_prestacion_paciente=prestacionPaciente.id,
                fecha_fin=today,
            )
            prestacionPacienteRepo.end_date(
                prestacionPaciente=prestacionPaciente,
                fecha_fin=today,
            )
            prestacionPacienteRepo.delete_by_activo(prestacion_paciente=prestacionPaciente)

        paciente_plan = pacientePlanRepo.filter_by_paciente_activo(id_paciente=id)
        if paciente_plan != None:
            pacientePlanRepo.delete_by_activo(paciente_plan=paciente_plan)
        
        today = date.today()
        cuota = cuotaRepo.filter_by_paciente_id_mes(id_paciente=id,year=today.year,month=today.month)
        if cuota:
            cuotaRepo.delete_by_activo(cuota=cuota)

        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=1, id_paciente=paciente.id)
        pacienteAreaRepo.delete_by_activo(paciente_area=pacienteArea)
        return redirect('pacientes_list', True)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteCreateFromExistent(View):
    http_method_names = ["post"]

    def post(self, request):
        dni = request.POST.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)
        user = request.user
        area = areaRepo.get_by_id(id=1)
        
        paciente_area = pacienteAreaRepo.create(
            id_paciente=paciente,
            id_area=area,
            id_usuario=user,
        )

        return redirect('paciente_detail', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteReactivate(View):
    http_method_names = ["post"]

    def post(self, request, id, area, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=area, id_paciente=paciente.id)
        pacienteAreaRepo.reactivate(pacienteArea)
        if area == 1:
            return redirect('paciente_detail', paciente.id)
        elif area == 2:
            return redirect('paciente_rehab_detail', paciente.id)
        elif area == 3:
            return redirect('paciente_fisiatria_detail', paciente.id)
        else:
            return redirect('inicio_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class ErrorPacienteExistente(View):

    def get(self, request):
        return render(
            request,
            'pacientes/error_paciente_existente.html',
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteRedirectFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)

        return redirect('paciente_detail', paciente.id)
