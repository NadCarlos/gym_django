from typing import List, Optional

from django.contrib.auth.models import User
from rehabilitacion.models import PacienteRehabilitacion, PacienteArea, EstadoCertificado, Derivador, ObraSocial



class PacienteRehabilitacionRepository:

    def get_all(self) -> List[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.all()
    
    def get_by_id(self, id: int) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.filter(id=id)
    
    def create(
        self,
        id_paciente_area: PacienteArea,
        nombre_tutor: str,
        celular_tutor:str,
        hijos: int,
        id_estado_certificado: EstadoCertificado,
        vencimiento_certificado: bool,
        fecha_junta: str,
        ven_presupuesto: bool,
        vencimiento_presupuesto: str,
        id_derivador: Derivador,
        puerto_esperanza: bool,
        id_obra_social:ObraSocial,
        id_usuario: User,
    ):
        return PacienteRehabilitacion.objects.create(
            id_paciente_area=id_paciente_area,
            nombre_tutor=nombre_tutor,
            celular_tutor=celular_tutor,
            hijos=hijos,
            id_estado_certificado=id_estado_certificado,
            vencimiento_certificado=vencimiento_certificado,
            fecha_junta=fecha_junta,
            ven_presupuesto=ven_presupuesto,
            vencimiento_presupuesto=vencimiento_presupuesto,
            id_derivador=id_derivador,
            puerto_esperanza=puerto_esperanza,
            id_obra_social=id_obra_social,
            id_usuario=id_usuario,
        )