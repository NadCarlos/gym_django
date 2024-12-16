from typing import List, Optional

from finanzas.models import Beneficiario


class BeneficiarioRepository:

    def get_all(self) -> List[Beneficiario]:
        return Beneficiario.objects.all()
    
    def filter_by_id(self) -> Optional[Beneficiario]:
        return Beneficiario.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Beneficiario]:
        return Beneficiario.objects.filter(
            activo=True
        ).order_by('nombre')
    
    def get_by_name(self, nombre: str) -> List[Beneficiario]:
        return Beneficiario.objects.get(
            nombre=nombre
        )
    
    def filter_by_numero_cuit(self, numero_cuit: str) -> List[Beneficiario]:
        return Beneficiario.objects.filter(
            numero_cuit=numero_cuit,
        ).first()
    
    def get_by_id(self, id: int) -> Optional[Beneficiario]:
        try:
            beneficiario = Beneficiario.objects.get(id=id)
        except:
            beneficiario = None
        return beneficiario
    
    def delete(self, beneficiario: Beneficiario):
        return beneficiario.delete()
    
    def delete_by_activo(self, beneficiario: Beneficiario):
        beneficiario.activo=False
        beneficiario.save()
    
    def create(
        self,
        nombre: str,
        numero_cuit: str,
    ):
        return Beneficiario.objects.create(
            nombre=nombre,
            numero_cuit=numero_cuit,
        )
    