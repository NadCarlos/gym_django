from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from rehabilitacion.models import PacienteRehabilitacion

from rehabilitacion.forms import(
    PacienteRehabilitacionCreateForm,
    PacienteRehabilitacionUpdateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.estado_certificado import EstadoCertificadoRepository
from rehabilitacion.repositories.derivador import DerivadorRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository

pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
estadoCertificadoRepo = EstadoCertificadoRepository()
derivadorRepo = DerivadorRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class RehabilitacionCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_area = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=id)
        derivador = derivadorRepo.filter_by_id(id=1)
        form = PacienteRehabilitacionCreateForm(initial={
            'id_usuario': request.user,
            'id_paciente_area': id_paciente_area.id,
            'id_derivador': derivador.id,
        })
        return render(
            request,
            'rehabilitacion/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = PacienteRehabilitacionCreateForm(request.POST)
        if form.is_valid():
            nombre_tutor_default = PacienteRehabilitacion._meta.get_field('nombre_tutor').default
            nombre_tutor = (form.cleaned_data.get('nombre_tutor') or nombre_tutor_default).upper()
            rehabilitacion_nueva = pacienteRehabRepo.create(
                id_paciente_area=form.cleaned_data['id_paciente_area'],
                nombre_tutor=nombre_tutor,
                celular_tutor=form.cleaned_data['celular_tutor'],
                hijos=form.cleaned_data['hijos'],
                id_estado_certificado=form.cleaned_data['id_estado_certificado'],
                vencimiento_certificado=form.cleaned_data['vencimiento_certificado'],
                fecha_junta=form.cleaned_data['fecha_junta'],
                ven_presupuesto=form.cleaned_data['ven_presupuesto'],
                vencimiento_presupuesto=form.cleaned_data['vencimiento_presupuesto'],
                id_derivador=form.cleaned_data['id_derivador'],
                puerto_esperanza=form.cleaned_data['puerto_esperanza'],
                id_obra_social=form.cleaned_data['id_obra_social'],
                id_conocer=form.cleaned_data['id_conocer'],
                id_usuario=form.cleaned_data['id_usuario'],
                diagnosticoCUD=form.cleaned_data['diagnosticoCUD'],
                pre_ingreso=form.cleaned_data['pre_ingreso'],
            )
            return redirect('paciente_rehab_detail', paciente.id)
        else:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class RehabilitacionUpdate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        form = PacienteRehabilitacionUpdateForm(instance=id_paciente_rehabilitacion)
        return render(
            request,
            'rehabilitacion/update.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        form = PacienteRehabilitacionUpdateForm(request.POST)
        if form.is_valid():
            nombre_tutor_default = PacienteRehabilitacion._meta.get_field('nombre_tutor').default
            nombre_tutor = (form.cleaned_data.get('nombre_tutor') or nombre_tutor_default).upper()
            pacienteRehabRepo.update(
                rehabilitacion_paciente=id_paciente_rehabilitacion,
                nombre_tutor=nombre_tutor,
                celular_tutor=form.cleaned_data['celular_tutor'],
                hijos=form.cleaned_data['hijos'],
                id_estado_certificado=form.cleaned_data['id_estado_certificado'],
                vencimiento_certificado=form.cleaned_data['vencimiento_certificado'],
                fecha_junta=form.cleaned_data['fecha_junta'],
                ven_presupuesto=form.cleaned_data['ven_presupuesto'],
                vencimiento_presupuesto=form.cleaned_data['vencimiento_presupuesto'],
                id_derivador=form.cleaned_data['id_derivador'],
                puerto_esperanza=form.cleaned_data['puerto_esperanza'],
                id_obra_social=form.cleaned_data['id_obra_social'],
                id_conocer=form.cleaned_data['id_conocer'],
                diagnosticoCUD=form.cleaned_data['diagnosticoCUD'],
                pre_ingreso=form.cleaned_data['pre_ingreso'],
            )
            return redirect('paciente_rehab_detail', paciente.id)
"""        else:
            return redirect('error')"""
