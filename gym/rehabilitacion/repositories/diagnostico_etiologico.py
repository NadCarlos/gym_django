from typing import List, Optional

from rehabilitacion.models import DiagnosticoEtiologico, TipoDiscapacidad


class DiagnosticoEtiologicoRepository:

    def get_all(self) -> List[DiagnosticoEtiologico]:
        return DiagnosticoEtiologico.objects.all()
    
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
        id_tipo_discapacidad: TipoDiscapacidad,
        ):
        return DiagnosticoEtiologico.objects.create(
            nombre=nombre,
            id_tipo_discapacidad=id_tipo_discapacidad,
        )