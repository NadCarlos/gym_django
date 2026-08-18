import json
from datetime import date, datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from administracion.filters import ProfesionalFilter

from administracion.forms import (
    ProfesionalCreateForm,
    ProfesionalUpdateForm,
    )

from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.sexo import SexoRepository
from administracion.repositories.localidad import LocalidadRepository
from administracion.repositories.profesional_area import ProfesionalAreaRepository
from administracion.repositories.area import AreaRepository
from rehabilitacion.repositories.asistencia_teorica import AsistenciaRehabTeoricaRepository

profesionalRepo = ProfesionalRepository()
sexoRepo = SexoRepository()
localidadRepo = LocalidadRepository()
profesionalAreaRepo = ProfesionalAreaRepository()
areaRepo = AreaRepository()
asistenciaTeoricaRepo = AsistenciaRehabTeoricaRepository()
REHABILITACION_AREA_ID = 2


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class ProfesionalRehabList(View):
    template_name = 'profesional_rehab/list.html'
    context_object_name = 'profesional_rehab'

    def get(self, request):

        filterset = ProfesionalFilter(
            request.GET,
            profesionalRepo.filter_profesional_area(id_area=REHABILITACION_AREA_ID),
        )
        
        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        # Obtener el queryset filtrado
        profesionales = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            profesionales = filterset.qs.order_by(ordering)

        profesionales_count = profesionales.count()

        return render(
            request,
            self.template_name,
            dict(
                profesionales=profesionales,
                profesionales_count=profesionales_count,
                form=filterset.form,
                ordering=ordering,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class HorasTeoricasProfesionalRehabList(View):
    template_name = 'profesional_rehab/horas_teoricas_list.html'

    ordering_fields = {
        'apellido': 'apellido',
        '-apellido': '-apellido',
        'nombre': 'nombre',
        '-nombre': '-nombre',
        'matricula': 'matricula',
        '-matricula': '-matricula',
        'total_horas': 'total_horas',
        '-total_horas': '-total_horas',
        'total_agendas': 'total_agendas',
        '-total_agendas': '-total_agendas',
    }

    def get(self, request):
        fecha_desde, fecha_hasta = self.get_rango_fechas(
            request.GET.get('fecha_desde'),
            request.GET.get('fecha_hasta'),
        )
        ordering = request.GET.get('ordering', '-total_horas')
        ordering = self.ordering_fields.get(ordering, '-total_horas')

        profesionales = asistenciaTeoricaRepo.horas_por_profesional(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            id_area=REHABILITACION_AREA_ID,
            ordering=ordering,
        )

        total_horas = sum(profesional['total_horas'] or 0 for profesional in profesionales)
        total_agendas = sum(profesional['total_agendas'] or 0 for profesional in profesionales)

        return render(
            request,
            self.template_name,
            dict(
                profesionales=profesionales,
                profesionales_count=profesionales.count(),
                total_horas=total_horas,
                total_agendas=total_agendas,
                fecha_desde=fecha_desde.strftime('%Y-%m-%d'),
                fecha_hasta=fecha_hasta.strftime('%Y-%m-%d'),
                rango_fechas=(
                    f"{fecha_desde.strftime('%d/%m/%Y')} al "
                    f"{fecha_hasta.strftime('%d/%m/%Y')}"
                ),
                ordering=ordering,
            )
        )

    def get_rango_fechas(self, fecha_desde, fecha_hasta):
        today = date.today()
        default_desde = today.replace(day=1)
        default_hasta = self.get_ultimo_dia_mes(default_desde)

        fecha_desde = self.get_fecha(fecha_desde, default_desde)
        fecha_hasta = self.get_fecha(fecha_hasta, default_hasta)

        if fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

        return fecha_desde, fecha_hasta

    def get_fecha(self, fecha, default):
        if fecha:
            try:
                return datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                pass
        return default

    def get_ultimo_dia_mes(self, fecha):
        if fecha.month == 12:
            primer_dia_siguiente_mes = date(fecha.year + 1, 1, 1)
        else:
            primer_dia_siguiente_mes = date(fecha.year, fecha.month + 1, 1)
        return date.fromordinal(primer_dia_siguiente_mes.toordinal() - 1)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class ProfesionalRehabDetail(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        return render(
            request,
            'profesional_rehab/detail.html',
            dict(
                profesional=profesional,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class ProfesionalRehabCreate(View):

    def get(self, request):
        profesionales_dni = profesionalRepo.dni_list_segun_area(state=True, id_area=1)
        sexo = sexoRepo.get_by_name(nombre="Masculino")
        localidad = localidadRepo.get_by_name(nombre="Rio Cuarto")
        form = ProfesionalCreateForm(initial = {
            'id_usuario': request.user,
            'id_sexo': sexo.id,
            'id_localidad': localidad.id
            }
        )
        return render(
            request,
            'profesional_rehab/create.html',
            dict(
                form=form,
                profesionales_dni=json.dumps(profesionales_dni),
            )
        )

    def post(self, request):
        form = ProfesionalCreateForm(request.POST)
        try:
            if form.is_valid():
                dni = form.cleaned_data['numero_dni']
                dni=int(dni)
                dniExistente = profesionalRepo.filter_by_dni(numero_dni=dni)
                matricula = form.cleaned_data['matricula']
                matriculaExistente = profesionalRepo.filter_by_matricula(matricula=matricula)
                if dniExistente is None and matriculaExistente is None:
                    area = areaRepo.get_by_id(id=2)
                    nombre = form.cleaned_data['nombre']
                    nombre = nombre.upper()
                    apellido = form.cleaned_data['apellido']
                    apellido = apellido.upper()
                    profesional_nuevo = profesionalRepo.create(
                        id_usuario=form.cleaned_data['id_usuario'],
                        nombre=nombre,
                        apellido=apellido,
                        numero_dni=form.cleaned_data['numero_dni'],
                        matricula=form.cleaned_data['matricula'],
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        id_sexo=form.cleaned_data['id_sexo'],
                        id_localidad=form.cleaned_data['id_localidad'],
                        direccion=form.cleaned_data['direccion'],
                        celular=form.cleaned_data['celular'],
                        email=form.cleaned_data['email'],
                        )
                    profesional_area = profesionalAreaRepo.create(
                        id_profesional=profesional_nuevo,
                        id_area=area,
                        id_usuario=form.cleaned_data['id_usuario'],
                    )
                    return redirect('profesional_rehab_detail', profesional_nuevo.id)
                else:
                    return redirect('error_profesional_existente')
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class ProfesionalRehabCreateFromExistent(View):

    def get(self, request):
        dni = request.GET.get('dni')
        dni = int(dni)
        profesional = profesionalRepo.get_by_dni(numero_dni=dni)
        user = request.user
        area = areaRepo.get_by_id(id=2)
        
        profesional_area = profesionalAreaRepo.create(
            id_profesional=profesional,
            id_area=area,
            id_usuario=user,
        )

        return redirect('profesional_rehab_detail', profesional.id)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class ProfesionalRehabUpdate(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        form = ProfesionalUpdateForm(instance=profesional)
        return render(
            request,
            'profesional_rehab/update.html',
            dict(
                form=form,
                profesional=profesional,
            )
        )

    def post(self, request, id):
        form = ProfesionalUpdateForm(request.POST)
        profesional = profesionalRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre = form.cleaned_data['nombre']
                nombre = nombre.upper()
                apellido = form.cleaned_data['apellido']
                apellido = apellido.upper()
                profesionalRepo.update(
                    profesional=profesional,
                    nombre=nombre,
                    apellido=apellido,
                    numero_dni=form.cleaned_data['numero_dni'],
                    matricula=form.cleaned_data['matricula'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    sexo=form.cleaned_data['id_sexo'],
                    localidad=form.cleaned_data['id_localidad'],
                    direccion=form.cleaned_data['direccion'],
                    celular=form.cleaned_data['celular'],
                    email=form.cleaned_data['email'],
                    )
                return redirect('profesional_rehab_detail', profesional.id)
        except:
            return redirect('error')
