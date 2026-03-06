from typing import List, Optional

from django.contrib.auth.models import User
from rehabilitacion.models import PacienteRehabilitacion, PacienteArea, EstadoCertificado, Derivador, ObraSocial, Conocer



class PacienteRehabilitacionRepository:

    def get_all(self) -> List[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.all()
    
    def get_by_id(self, id: int) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.filter(id=id)
    
    def get_by_paciente_id(self, id_paciente) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.filter(id_paciente_area__id_paciente__id=id_paciente).filter(activo=True).exists()
    
    def get_by_paciente_id_item(self, id_paciente) -> Optional[PacienteRehabilitacion]:
        return PacienteRehabilitacion.objects.filter(id_paciente_area__id_paciente__id=id_paciente).filter(activo=True).first()
    
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
        id_conocer: Conocer,
        id_usuario: User,
        diagnosticoCUD: str,
        pre_ingreso: bool,
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
            id_conocer=id_conocer,
            id_usuario=id_usuario,
            diagnosticoCUD=diagnosticoCUD,
            pre_ingreso=pre_ingreso,
        )
    
    def update(
        self,
        rehabilitacion_paciente: PacienteRehabilitacion,
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
        id_conocer: Conocer,
        diagnosticoCUD: str,
        pre_ingreso: bool,
    )-> PacienteRehabilitacion:
        
        rehabilitacion_paciente.nombre_tutor=nombre_tutor
        rehabilitacion_paciente.celular_tutor=celular_tutor
        rehabilitacion_paciente.hijos=hijos
        rehabilitacion_paciente.id_estado_certificado=id_estado_certificado
        rehabilitacion_paciente.vencimiento_certificado=vencimiento_certificado
        rehabilitacion_paciente.fecha_junta=fecha_junta
        rehabilitacion_paciente.ven_presupuesto=ven_presupuesto
        rehabilitacion_paciente.vencimiento_presupuesto=vencimiento_presupuesto
        rehabilitacion_paciente.id_derivador=id_derivador
        rehabilitacion_paciente.puerto_esperanza=puerto_esperanza
        rehabilitacion_paciente.id_obra_social=id_obra_social
        rehabilitacion_paciente.id_conocer=id_conocer
        rehabilitacion_paciente.diagnosticoCUD=diagnosticoCUD
        rehabilitacion_paciente.pre_ingreso=pre_ingreso

        rehabilitacion_paciente.save()
