from typing import List, Optional

from rehabilitacion.models import Informe
from rehabilitacion.repositories.archivo import ArchivoRepository
from rehabilitacion.repositories.link import LinkRepository
from administracion.models import Paciente, Profesional, ProfesionalTratamiento


class InformeRepository:
    archivo_repo = ArchivoRepository()
    link_repo = LinkRepository()

    def get_all(self) -> List[Informe]:
        return Informe.objects.all()

    def get_by_id(self, id: int) -> Optional[Informe]:
        return Informe.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Informe]:
        return Informe.objects.filter(id=id, activo=True).first()
    
    def filter_by_paciente_id(self, paciente_id) -> Optional[Informe]:
        return Informe.objects.filter(id_paciente=paciente_id, activo=True)
    
    def create(
        self,
        fecha: str,
        id_profesional: Profesional,
        id_profesional_tratamiento: ProfesionalTratamiento,
        id_paciente: Paciente,
        observaciones: str,
        ):
        return Informe.objects.create(
            fecha=fecha,
            id_profesional=id_profesional,
            id_profesional_tratamiento=id_profesional_tratamiento,
            id_paciente=id_paciente,
            observaciones=observaciones,
        )

    def delete(self, informe: Informe):
        archivos = self.archivo_repo.filter_by_informe_id(informe_id=informe.id)
        links = self.link_repo.filter_by_informe_id(informe_id=informe.id)
        for archivo in archivos:
            self.archivo_repo.delete(archivo=archivo)
        for link in links:
            self.link_repo.delete(link=link)
        informe.activo = False
        informe.save(update_fields=["activo"])
        return informe
