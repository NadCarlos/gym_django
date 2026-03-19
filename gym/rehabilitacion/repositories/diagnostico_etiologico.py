from typing import List, Optional

from rehabilitacion.models import Alta, DiagnosticoEtiologico, TipoDiscapacidad
from rehabilitacion.repositories.alta_etiologico import AltaEtiologicoRepository


altaEtiologicoRepo = AltaEtiologicoRepository()


class DiagnosticoEtiologicoRepository:

    def get_all(self) -> List[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.all().order_by("nombre")
    
    def get_all_dict(self) -> dict:
        diagnosticos = DiagnosticoEtiologico.objects.all()
        diagnosticos_dict = {}

        for d in diagnosticos:
            key = str(d.id_tipo_discapacidad.id)
            diagnosticos_dict.setdefault(key, []).append({
                "id": d.id,
                "nombre": d.nombre
            })

        return diagnosticos_dict

    
    def get_by_id(self, id: int) -> Optional[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.filter(id=id)
    
    def filter_by_tipo_discapacidad_id(self, id_tipo_discapacidad) -> Optional[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.filter(id_tipo_discapacidad=id_tipo_discapacidad).first()
    
    def filter_by_tipo_discapacidad_id_list(self, id_tipo_discapacidad) -> Optional[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.filter(id_tipo_discapacidad=id_tipo_discapacidad).values("id", "nombre")
    
    def create(
        self,
        nombre: str,
        id_tipo_discapacidad: Optional[TipoDiscapacidad] = None,
        ):
        return DiagnosticoEtiologico.objects.create(
            nombre=nombre,
            id_tipo_discapacidad=id_tipo_discapacidad,
        )

    def update(
        self,
        diagnostico_etiologico: DiagnosticoEtiologico,
        nombre: str,
        id_tipo_discapacidad: Optional[TipoDiscapacidad] = None,
    ):
        diagnostico_etiologico.nombre = nombre
        diagnostico_etiologico.id_tipo_discapacidad = id_tipo_discapacidad
        diagnostico_etiologico.save()
        return diagnostico_etiologico

    def has_diagnostico_funcional_relation(self, diagnostico_etiologico: DiagnosticoEtiologico) -> bool:
        return diagnostico_etiologico.id_diagnostico_etiologico_en_funcional.exists()

    def has_alta_relation(self, diagnostico_etiologico: DiagnosticoEtiologico) -> bool:
        return (
            Alta.objects.filter(id_diagnostico_etiologico=diagnostico_etiologico).exists()
            or altaEtiologicoRepo.has_active_diagnostico_relation(diagnostico_etiologico)
        )

    def delete(self, diagnostico_etiologico: DiagnosticoEtiologico):
        diagnostico_etiologico.delete()
