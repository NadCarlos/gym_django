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


def nombres_relacionados(relaciones, attr_name):
    nombres = []
    for relacion in relaciones:
        objeto_relacionado = getattr(relacion, attr_name, None)
        if objeto_relacionado is not None:
            nombres.append(objeto_relacionado.nombre)
    return ", ".join(nombres)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacientesRehabBulkAdd(View):
    def get(self, request):
        return render(
            request,
            'pacientes_rehab/bulk_add.html',
        )
    
    def post(self, request):
        try:
            file = request.FILES['file']
        except:
            return redirect('error')
        excel = pd.read_excel(file)

        # [0]=id???,[1]=apellido,[2]=nombre,[3]=documento,[4]=direccion,[5]=telefono,[6]=celular,[7]=localidad,[8]=f.nac,[9]=idOSoc,[10]=eCiv,[11]=ideCiv,[12]=sex
        for data in excel.values:
            documento = data[3]
            
            paciente = pacienteRepo.filter_by_dni(numero_dni=documento, id_area=2)
            id_obra_social = data[9]
            id_estado_civil = data[11]

            try:
                obra_social = obraSocialRepo.get_by_name(nombre=id_obra_social)
            except:
                obra_social = None
            
            try:
                estado_civil = estadoCivilRepo.get_by_name(nombre=id_estado_civil)
            except:
                estado_civil = None

            pacienteRepo.update_o_soc_e_civ(
                paciente=paciente,
                obra_social=obra_social,
                estado_civil=estado_civil,
            )

        return redirect('inicio_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteRehabDetail(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        altas = []
        tiene_pendientes=False
        altas_funcionales = []
        if rehabilitacion_paciente != None:
            altas = altaRepo.filter_by_paciente_rehab_id(id_paciente_rehab=rehabilitacion_paciente.id)
            tiene_pendientes = altaRepo.tiene_alta_activa(id_paciente_rehab=rehabilitacion_paciente.id)
            for alta in altas:
                alta.altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_all_by_alta_id(alta_id=alta.id)
                alta.altas_etiologicos = altaEtiologicoRepo.filter_all_by_alta_id(alta_id=alta.id)
                alta.altas_funcionales = altaFuncionalRepo.filter_all_by_alta_id(alta_id=alta.id)
                if not alta.dado_alta:
                    altas_funcionales.extend(alta.altas_funcionales)
        return render(
            request,
            'pacientes_rehab/detail.html',
            dict(
                paciente=paciente,
                rehabilitacion_paciente=rehabilitacion_paciente,
                altas=altas,
                tiene_pendientes=tiene_pendientes,
                altas_funcionales=altas_funcionales,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteRehabCreate(View):

    def get(self, request):
        pacientes_dni = pacienteRepo.dni_list_segun_area(id_area=1)
        pacientes_dni_area_actual = pacienteRepo.dni_list_segun_area(id_area=2)
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
                pacientes_dni_area_actual=json.dumps(pacientes_dni_area_actual),
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
                    email=form.cleaned_data['email'],
                    observaciones=form.cleaned_data['observaciones'],
                    )
                paciente_area = pacienteAreaRepo.create(
                    id_paciente=paciente_nuevo,
                    id_area=area,
                    id_usuario=form.cleaned_data['id_usuario'],
                )
                return redirect('paciente_rehab_detail', paciente_nuevo.id)
            else:
                return redirect('error_paciente_existente')
        else:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
                        email=form.cleaned_data['email'],
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
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteRehabDelete(View):

    def get(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        today = date.today()
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)
        agendas = agendaRepo.filter_by_paciente_area(id_paciente_area=pacienteArea.id)
        if agendas != None:
            for agenda in agendas:
                agendaRepo.end_date(
                    agenda=agenda,
                    fecha_fin=today,
                )
                agendaRepo.delete_by_activo(agenda=agenda)

        paciente_plan = pacientePlanRepo.filter_by_paciente_activo(id_paciente=id)
        if paciente_plan != None:
            pacientePlanRepo.delete_by_activo(paciente_plan=paciente_plan)
        
        """cuota = cuotaRepo.filter_by_paciente_id_mes(id_paciente=id,year=today.year,month=today.month)
        if cuota:
            cuotaRepo.delete_by_activo(cuota=cuota)"""

        pacienteRepo.delete_by_activo(paciente=paciente)
        return redirect('pacientes_rehab_list', True)
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteRehabToCsv(View):

    def get(self, request, id):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=paciente_detail.xlsx'

        paciente = pacienteRepo.get_by_id(id=id)
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)

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
            paciente.id_obra_social.nombre if paciente.id_obra_social else '',
            paciente.id_estado_civil.nombre if paciente.id_estado_civil else '',
            paciente.id_localidad.nombre if paciente.id_localidad else '',
            paciente.id_sexo.nombre if paciente.id_sexo else '',
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
        if rehabilitacion_paciente is not None:
            data_paciente_rehabilitacion.append([
                rehabilitacion_paciente.nombre_tutor,
                rehabilitacion_paciente.celular_tutor,
                rehabilitacion_paciente.hijos,
                rehabilitacion_paciente.id_estado_certificado.nombre if rehabilitacion_paciente.id_estado_certificado else '',
                rehabilitacion_paciente.vencimiento_certificado,
                rehabilitacion_paciente.fecha_junta,
                rehabilitacion_paciente.vencimiento_presupuesto,
                rehabilitacion_paciente.id_derivador.nombre if rehabilitacion_paciente.id_derivador else '',
                rehabilitacion_paciente.id_conocer.nombre if rehabilitacion_paciente.id_conocer else '',
                rehabilitacion_paciente.id_obra_social.nombre if rehabilitacion_paciente.id_obra_social else '',
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
            'Conocio por',
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteAltasToCsv(View):

    def get(self, request, id):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=altas_paciente.xlsx'

        paciente = pacienteRepo.get_by_id(id=id)
        rehabilitacion_paciente = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        altas = altaRepo.filter_by_paciente_rehab_id(id_paciente_rehab=rehabilitacion_paciente.id)

        data = []
        for alta in altas:
            altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_all_by_alta_id(alta_id=alta.id)
            altas_etiologicos = altaEtiologicoRepo.filter_all_by_alta_id(alta_id=alta.id)
            altas_funcionales = altaFuncionalRepo.filter_all_by_alta_id(alta_id=alta.id)
            data.append([
                alta.fecha,
                nombres_relacionados(altas_etiologicos, 'id_diagnostico_etiologico'),
                nombres_relacionados(altas_tipo_discapacidad, 'id_tipo_discapacidad'),
                nombres_relacionados(altas_funcionales, 'id_diagnostico_funcional'),
                alta.dado_alta,
                alta.fecha_alta,
                ])

        df = pd.DataFrame(data, columns=[
            'Fecha',
            'Diagnosticos Etiologicos',
            'Tipos Discapacidad',
            'Diagnosticos Funcionales',
            'Dado Alta',
            'Fecha Alta',
            ])

        alta_activa = altaRepo.filter_by_id_activa(id_paciente_rehab=rehabilitacion_paciente.id)
        data_tipos_discapacidad = []
        data_diagnosticos_etiologicos = []
        data_diagnosticos_funcionales = []
        if alta_activa is not None:
            altas_tipo_discapacidad = altaTipoDiscapacidadRepo.filter_by_alta_id(alta_id=alta_activa.id)
            for alta_tipo_discapacidad in altas_tipo_discapacidad:
                data_tipos_discapacidad.append([
                    alta_tipo_discapacidad.id_tipo_discapacidad.nombre,
                    alta_tipo_discapacidad.observaciones,
                ])

            altas_etiologicos = altaEtiologicoRepo.filter_by_alta_id(alta_id=alta_activa.id)
            for alta_etiologico in altas_etiologicos:
                data_diagnosticos_etiologicos.append([
                    alta_etiologico.id_diagnostico_etiologico.nombre,
                    alta_etiologico.observaciones,
                ])

            altas_funcionales = altaFuncionalRepo.filter_by_alta_id(alta_id=alta_activa.id)
            for alta_funcional in altas_funcionales:
                data_diagnosticos_funcionales.append([
                    alta_funcional.id_diagnostico_funcional.nombre,
                    alta_funcional.observaciones,
                ])

        df_tipos_discapacidad = pd.DataFrame(
            data_tipos_discapacidad,
            columns=[
                'Tipo Discapacidad',
                'Observaciones',
            ],
        )

        df_diagnosticos_etiologicos = pd.DataFrame(
            data_diagnosticos_etiologicos,
            columns=[
                'Diagnostico Etiologico',
                'Observaciones',
            ],
        )

        df_diagnosticos_funcionales = pd.DataFrame(
            data_diagnosticos_funcionales,
            columns=[
                'Diagnostico Funcional',
                'Observaciones',
            ],
        )
        
        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Altas', index=False)
            df_tipos_discapacidad.to_excel(
                writer,
                sheet_name='Tipos discapacidad',
                index=False,
            )
            df_diagnosticos_etiologicos.to_excel(
                writer,
                sheet_name='Diag etiologicos',
                index=False,
            )
            df_diagnosticos_funcionales.to_excel(
                writer,
                sheet_name='Diagnosticos funcionales',
                index=False,
            )

        response.write(output.getvalue())

        return response
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteRehabRedirectFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)

        return redirect('paciente_rehab_detail', paciente.id)
