from typing import List, Optional

from rehabilitacion.models import TipoDiscapacidad
from rehabilitacion.repositories.alta_tipo_discapacidad import AltaTipoDiscapacidadRepository


altaTipoDiscapacidadRepo = AltaTipoDiscapacidadRepository()


class TipoDiscapacidadRepository:

    def get_all(self) -> List[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.all().order_by("nombre")
    
    def get_by_id(self, id: int) -> Optional[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.get(id=id)

    def filter_by_id(self, id: int) -> Optional[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.filter(id=id).first()
    
    def filter_by_diagnostico_etiologico_id(self, id_diagnostico_etiologico) -> Optional[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico).first()

    def create(
        self,
        nombre: str,
    ):
        return TipoDiscapacidad.objects.create(
            nombre=nombre,
        )

    def update(
        self,
        tipo_discapacidad: TipoDiscapacidad,
        nombre: str,
    ):
        tipo_discapacidad.nombre = nombre
        tipo_discapacidad.save()
        return tipo_discapacidad

    def delete(self, tipo_discapacidad: TipoDiscapacidad):
        tipo_discapacidad.delete()

    def has_alta_relation(self, tipo_discapacidad: TipoDiscapacidad) -> bool:
        return altaTipoDiscapacidadRepo.has_active_tipo_relation(tipo_discapacidad)
