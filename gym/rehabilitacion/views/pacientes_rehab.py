from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

import json
import pandas as pd
import io

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
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository


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
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()


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
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        altas = "None"
        tiene_pendientes=False
        if rehabilitacion_paciente != None:
            altas = altaRepo.filter_by_paciente_rehab_id(id_paciente_rehab=rehabilitacion_paciente.id)
            tiene_pendientes = altaRepo.tiene_alta_activa(id_paciente_rehab=rehabilitacion_paciente.id)
        return render(
            request,
            'pacientes_rehab/detail.html',
            dict(
                paciente=paciente,
                rehabilitacion_paciente=rehabilitacion_paciente,
                altas=altas,
                tiene_pendientes=tiene_pendientes,
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
class PacienteRehabUpdate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PacienteUpdateForm(instance=paciente)
        return render(
            request,
            'pacientes_rehab/update.html',
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
                        observaciones=form.cleaned_data['observaciones'],
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        obra_social=form.cleaned_data['id_obra_social'],
                        estado_civil=form.cleaned_data['id_estado_civil'],
                        sexo=form.cleaned_data['id_sexo'],
                        localidad=form.cleaned_data['id_localidad'],
                        )
                    return redirect('paciente_rehab_detail', paciente.id)
                else:
                    return redirect('error_paciente_existente')
        except:
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


@method_decorator(login_required(login_url='login'), name='dispatch')
class PacienteRehabToCsv(View):

    def get(self, request, id):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=paciente_detail.xlsx'

        paciente = pacienteRepo.get_by_id(id=id)
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        altas = altaRepo.filter_by_paciente_rehab_id(id_paciente_rehab=rehabilitacion_paciente.id)
        tiene_pendientes = altaRepo.tiene_alta_activa()

        data_paciente = []
        data_paciente.append([
            paciente.nombre,
            paciente.apellido,
            paciente.numero_dni,
            paciente.direccion,
            paciente.telefono,
            paciente.celular,
            paciente.fecha_nacimiento,
            paciente.observaciones,
            paciente.activo,
            paciente.id_obra_social.nombre,
            paciente.id_estado_civil.nombre,
            paciente.id_localidad.nombre,
            paciente.id_sexo.nombre,
            ])

        df = pd.DataFrame(data_paciente, columns=[
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
            ])
        
        data_paciente_rehabilitacion = []
        data_paciente_rehabilitacion.append([
            rehabilitacion_paciente.nombre_tutor,
            rehabilitacion_paciente.celular_tutor,
            rehabilitacion_paciente.hijos,
            rehabilitacion_paciente.id_estado_certificado.nombre,
            rehabilitacion_paciente.vencimiento_certificado,
            rehabilitacion_paciente.fecha_junta,
            rehabilitacion_paciente.vencimiento_presupuesto,
            rehabilitacion_paciente.id_derivador.nombre,
            rehabilitacion_paciente.id_obra_social.nombre,
            rehabilitacion_paciente.puerto_esperanza,
        ])
        
        df_rehab = pd.DataFrame(data_paciente_rehabilitacion, columns=[
            'Nombre Tutor',
            'Celular',
            'Hijos',
            'Estado Certificado',
            'Vencimiento Certificado',
            'Fecha Junta',
            'Vto Presupuesto',
            'Derivador',
            'obra social',
            'Puerto Esperanza',
            ])

        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Paciente', index=False)
            df_rehab.to_excel(writer, sheet_name='Datos Rehabilitacion', index=False)

        response.write(output.getvalue())

        return response
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacienteAltasToCsv(View):

    def get(self, request, id):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=altas_paciente.xlsx'

        paciente = pacienteRepo.get_by_id(id=id)
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        altas = altaRepo.filter_by_paciente_rehab_id(id_paciente_rehab=rehabilitacion_paciente.id)

        data = []
        for alta in altas:
            data.append([
                alta.fecha,
                alta.id_diagnostico.nombre,
                alta.fecha_alta,
                alta.dado_alta,
                ])

        df = pd.DataFrame(data, columns=[
            'Fecha',
            'Diagnostico',
            'Dado Alta',
            'Fecha Alta',
            ])
        
        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Altas', index=False)

        response.write(output.getvalue())

        return response
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class PacientesAltasToCreateOnlyUseOnce(View):
    def get(self, request):
        pacientes = pacienteRepo.get_all_2()
        area=areaRepo.get_by_id(id=1)
        user = request.user
        for paciente in pacientes:
            pacienteAreaRepo.create(
                    id_paciente=paciente,
                    id_area=area,
                    id_usuario=user,
                )
        total = len(pacientes)

        return render(
            request,
            'pacientes_rehab/to_delete.html',
            dict(
                total=total,
            )
        )