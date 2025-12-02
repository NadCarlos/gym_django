from typing import List, Optional

from rehabilitacion.models import DiagnosticoFuncional, DiagnosticoEtiologico


class DiagnosticoFuncionalRepository:

    def get_all(self) -> List[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.all()
    
    def get_by_id(self, id: int) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id=id).first()
    
    def filter_by_tipo_diagnostico_etiologico_id(self, id_diagnostico_etiologico) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico)
    
    def filter_by_tipo_diagnostico_etiologico_id_list(self, id_diagnostico_etiologico) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico).values("id", "nombre")
    
    def create(
        self,
        nombre: str,
        id_diagnostico_etiologico: DiagnosticoEtiologico,
        ):
        return DiagnosticoFuncional.objects.create(
            nombre=nombre,
            id_diagnostico_etiologico=id_diagnostico_etiologico,
        )