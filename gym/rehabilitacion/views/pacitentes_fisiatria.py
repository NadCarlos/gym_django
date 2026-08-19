from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import OperationalError
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

import json
from datetime import datetime, date

from administracion.filters import PacienteFisiatriaFilter

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
from rehabilitacion.models import Turno


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
        filterset = PacienteFisiatriaFilter(request.GET, pacienteRepo.filter_pacientes_area(state, id_area=3))
        fecha_inicio = self.get_fecha(request.GET.get('fecha_inicio'), date.today())
        fecha_fin = self.get_fecha(request.GET.get('fecha_fin'))

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        pacientes = filterset.qs
        if ordering:
            pacientes = pacientes.order_by(ordering)

        turnos_cercanos = Turno.objects.filter(activo=True).select_related(
            "profesional_id",
            "tratamiento_id",
        ).order_by("fecha", "hora")
        if fecha_inicio:
            turnos_cercanos = turnos_cercanos.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            turnos_cercanos = turnos_cercanos.filter(fecha__lte=fecha_fin)

        pacientes = pacientes.prefetch_related(
            Prefetch(
                "turnos_rehabilitacion",
                queryset=turnos_cercanos,
                to_attr="turnos_cercanos",
            )
        )
        pacientes_count = pacientes.count()

        for paciente in pacientes:
            paciente.turno = (
                paciente.turnos_cercanos[0]
                if paciente.turnos_cercanos
                else None
            )

        return render(
            request,
            self.template_name,
            dict(
                pacientes_count = pacientes_count,
                pacientes=pacientes,
                form=filterset.form,
                ordering=ordering,
                state=state,
                fecha_inicio=fecha_inicio.isoformat() if fecha_inicio else '',
                fecha_fin=fecha_fin.isoformat() if fecha_fin else '',
            )
        )

    def get_fecha(self, fecha, default=None):
        if not fecha:
            return default
        try:
            return datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return default


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class PacienteFisiatriaDetail(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=3, id_paciente=paciente.id)
        return render(
            request,
            'pacientes_fisiatria/detail.html',
            dict(
                paciente=paciente,
                pacienteArea=pacienteArea,
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
        if not form.is_valid():
            return redirect('error')

        area = areaRepo.get_by_id(id=3)
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
        return redirect('paciente_fisiatria_detail', paciente.id)
        

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
        except OperationalError:
            raise
        except Exception:
            return redirect('error')
        return render(
            request,
            'pacientes_fisiatria/update.html',
            dict(
                form=form,
                paciente=paciente,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaCreateFromExistent(View):
    http_method_names = ["post"]

    def post(self, request):
        dni = request.POST.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)
        if paciente is None:
            return redirect('error')
        user = request.user
        area = areaRepo.get_by_id(id=3)
        
        paciente_area = pacienteAreaRepo.create(
            id_paciente=paciente,
            id_area=area,
            id_usuario=user,
        )

        return redirect('paciente_fisiatria_detail', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class PacienteFisiatriaRedirectFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        paciente = pacienteRepo.get_by_dni(numero_dni=dni)
        if paciente is None:
            return redirect('error')

        return redirect('paciente_fisiatria_detail', paciente.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PacienteFisiatriaDelete(View):
    http_method_names = ["post"]

    def post(self, request, id, *args, **kwargs):
        paciente = pacienteRepo.get_by_id(id=id)
        if paciente is None:
            return redirect('error')
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=3, id_paciente=paciente.id)
        if pacienteArea is None:
            return redirect('error')
        pacienteAreaRepo.delete_by_activo(paciente_area=pacienteArea)
        return redirect('pacientes_fisiatria_list', True)