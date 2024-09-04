from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import PrestacionPaciente, Paciente, ObraSocial, Prestacion


class PrestacionPacienteRepository:

    def get_all(self) -> List[PrestacionPaciente]:
        return PrestacionPaciente.objects.all()
    
    def filter_by_id(self, id) -> Optional[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(id=id).latest()
    
    def filter_by_id_paciente(self, id_paciente) -> Optional[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(id_paciente=id_paciente).first()
    
    def filter_by_id_paciente_all(self, id_paciente) -> Optional[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(id_paciente=id_paciente).all().order_by('-activo')
    
    def filter_by_id_paciente_activo(self, id_paciente) -> Optional[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(id_paciente=id_paciente).filter(activo=True)
    
    def filter_by_activo(self) -> List[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(
            activo=True
        )
    
    def get_by_id(self, id: int) -> Optional[PrestacionPaciente]:
        try:
            prestacion_paciente = PrestacionPaciente.objects.get(id=id)
        except:
            prestacion_paciente = None
        return prestacion_paciente
    
    def get_by_paciente_id(self, id_paciente: int) -> Optional[PrestacionPaciente]:
        try:
            prestacion_paciente = PrestacionPaciente.objects.get(id_paciente=id_paciente)
        except:
            prestacion_paciente = None
        return prestacion_paciente
    
    def delete(self, prestacion_paciente: PrestacionPaciente):
        return prestacion_paciente.delete()
    
    def delete_by_activo(self, prestacion_paciente: PrestacionPaciente):
        prestacion_paciente.activo=False
        prestacion_paciente.save()
    
    def create(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        prestacion: Prestacion,
        paciente: Paciente,
        obraSocial: ObraSocial,
    ):
        return PrestacionPaciente.objects.create(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_prestacion=prestacion,
            id_paciente=paciente,
            id_obra_social=obraSocial,
        )