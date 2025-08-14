from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from rehabilitacion.forms import (
    AltaCreateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.diagnostico import DiagnosticoRepository
from rehabilitacion.repositories.familia import FamiliaRepository


pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
altaRepo = AltaRepository()
diagnosticoRepo = DiagnosticoRepository()
familiaRepo = FamiliaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AltaCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        id_paciente_rehabilitacion = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=id)
        form = AltaCreateForm(initial={'id_paciente_rehabilitacion':id_paciente_rehabilitacion.id})
        return render(
            request,
            'alta/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request, id):
        form = AltaCreateForm(request.POST)
        if form.is_valid():
            hay_diagnostico_nuevo = request.POST.get('id_diagnostico')
            fecha=form.cleaned_data['fecha']
            id_paciente_rehabilitacion=form.cleaned_data['id_paciente_rehabilitacion']
            id_diagnostico=form.cleaned_data['id_diagnostico']
            id_familia=form.cleaned_data['id_familia']
            if hay_diagnostico_nuevo == "nuevo":
                nombre_nuevo_diagnostico = request.POST.get('nuevo_diagnostico')
                diagnostico_nuevo = diagnosticoRepo.create(
                    id_familia=id_familia,
                    nombre=nombre_nuevo_diagnostico,
                )
                nueva_alta = altaRepo.create(
                    fecha=fecha,
                    id_paciente_rehabilitacion=id_paciente_rehabilitacion,
                    id_diagnostico=diagnostico_nuevo.id,
                )
                return redirect('pacientes_rehab_list', id)
            else:
                diagnostico_correcto = diagnosticoRepo.filter_by_familia_id(id_familia=id_familia)
                nueva_alta = altaRepo.create(
                    fecha=fecha,
                    id_paciente_rehabilitacion=id_paciente_rehabilitacion,
                    id_diagnostico=diagnostico_correcto, #YEA SOMETHING BAD AT HOW THIS IS MANAGED
                )
                return redirect('pacientes_rehab_list', id)
