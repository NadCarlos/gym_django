from typing import List, Optional

from rehabilitacion.models import DiagnosticoFuncional, DiagnosticoEtiologico, AltaFuncional


class DiagnosticoFuncionalRepository:

    def get_all(self) -> List[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.all().order_by("nombre")
    
    def get_by_id(self, id: int) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id=id).first()
    
    def filter_by_tipo_diagnostico_etiologico_id(self, id_diagnostico_etiologico) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico)
    
    def filter_by_tipo_diagnostico_etiologico_id_list(self, id_diagnostico_etiologico) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico).values("id", "nombre")

    def get_all_list(self) -> Optional[DiagnosticoFuncional]:
        return DiagnosticoFuncional.objects.values("id", "nombre").order_by("nombre")
    
    def create(
        self,
        nombre: str,
        id_diagnostico_etiologico: Optional[DiagnosticoEtiologico] = None,
        ):
        return DiagnosticoFuncional.objects.create(
            nombre=nombre,
            id_diagnostico_etiologico=id_diagnostico_etiologico,
        )

    def update(
        self,
        diagnostico_funcional: DiagnosticoFuncional,
        nombre: str,
        id_diagnostico_etiologico: Optional[DiagnosticoEtiologico] = None,
    ):
        diagnostico_funcional.nombre = nombre
        diagnostico_funcional.id_diagnostico_etiologico = id_diagnostico_etiologico
        diagnostico_funcional.save()
        return diagnostico_funcional

    def has_alta_funcional_relation(self, diagnostico_funcional: DiagnosticoFuncional) -> bool:
        return AltaFuncional.objects.filter(
            id_diagnostico_funcional=diagnostico_funcional,
            activo=True,
        ).exists()

    def delete(self, diagnostico_funcional: DiagnosticoFuncional):
        diagnostico_funcional.delete()
