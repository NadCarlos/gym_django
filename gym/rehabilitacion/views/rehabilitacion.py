from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from rehabilitacion.forms import(
    PacienteRehabilitacionCreateForm,
)

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.estado_certificado import EstadoCertificadoRepository
from rehabilitacion.repositories.derivador import DerivadorRepository

pacienteRepo = PacienteRepository()
pacienteAreaRepo = PacienteAreaRepository()
estadoCertificadoRepo = EstadoCertificadoRepository()
derivadorRepo = DerivadorRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
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