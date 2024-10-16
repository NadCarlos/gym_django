from typing import List, Optional

from administracion.models import ProfesionalTratamiento, Tratamiento, Profesional


class TratamientoProfesionalRepository:

    def get_all(self) -> List[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.all()
    
    def filter_by_id(self, id) -> Optional[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.filter(id=id).latest()
    
    def filter_by_id_profesional(self, id_profesional) -> Optional[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.filter(id_profesional=id_profesional).first()
    
    def filter_by_id_profesional_all(self, id_profesional) -> Optional[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.filter(id_profesional=id_profesional).all()
    
    def filter_by_id_profesional_activo(self, id_profesional) -> Optional[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.filter(id_profesional=id_profesional).filter(activo=True)
    
    def filter_by_activo(self) -> List[ProfesionalTratamiento]:
        return ProfesionalTratamiento.objects.filter(
            activo=True
        )
    
    def get_by_id(self, id: int) -> Optional[ProfesionalTratamiento]:
        try:
            profesional_tratamiento = ProfesionalTratamiento.objects.get(id=id)
        except:
            profesional_tratamiento = None
        return profesional_tratamiento
    
    def get_by_paciente_id(self, id_profesional: int) -> Optional[ProfesionalTratamiento]:
        try:
            profesional_tratamiento = ProfesionalTratamiento.objects.get(id_profesional=id_profesional)
        except:
            profesional_tratamiento = None
        return profesional_tratamiento
    
    def delete(self, profesional_tratamiento: ProfesionalTratamiento):
        return profesional_tratamiento.delete()
    
    def delete_by_activo(self, profesional_tratamiento: ProfesionalTratamiento):
        profesional_tratamiento.activo=False
        profesional_tratamiento.save()
    
    def create(
        self,
        fecha_inicio: str,
        tratamiento: Tratamiento,
        profesional: Profesional,
    ):
        return ProfesionalTratamiento.objects.create(
            fecha_inicio=fecha_inicio,
            id_tratamiento=tratamiento,
            id_profesional=profesional,
        )
    
    def update(
        self, 
        tratamientoProfesional: ProfesionalTratamiento,
        fecha_inicio: str,
        tratamiento: Tratamiento,
        profesional: Profesional,
    ) -> ProfesionalTratamiento:

        tratamientoProfesional.fecha_inicio = fecha_inicio
        tratamientoProfesional.id_tratamiento = tratamiento
        tratamientoProfesional.id_profesional = profesional

        tratamientoProfesional.save()