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
        return PrestacionPaciente.objects.filter(id_paciente=id_paciente).all().order_by('-fecha_inicio')
    
    def filter_by_id_paciente_activo(self, id_paciente) -> Optional[PrestacionPaciente]:
        return PrestacionPaciente.objects.filter(id_paciente=id_paciente).filter(activo=True).first()
    
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
        prestacion: Prestacion,
        paciente: Paciente,
        obraSocial: ObraSocial,
    ):
        return PrestacionPaciente.objects.create(
            fecha_inicio=fecha_inicio,
            id_prestacion=prestacion,
            id_paciente=paciente,
            id_obra_social=obraSocial,
        )
    
    def update(
        self, 
        prestacionPaciente: PrestacionPaciente,
        fecha_inicio: str,
        fecha_fin: str,
        id_prestacion: Prestacion,
        id_obra_social: ObraSocial,
    ) -> PrestacionPaciente:

        prestacionPaciente.fecha_inicio = fecha_inicio
        prestacionPaciente.fecha_fin = fecha_fin
        prestacionPaciente.id_prestacion = id_prestacion
        prestacionPaciente.id_obra_social = id_obra_social

        prestacionPaciente.save()

    def end_date(
        self,
        prestacionPaciente: PrestacionPaciente,
        fecha_fin: str,
    ) -> PrestacionPaciente:

        prestacionPaciente.fecha_fin = fecha_fin

        prestacionPaciente.save()