from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import ObraSocial


class ObraSocialRepository:

    def get_all(self) -> List[ObraSocial]:
        return ObraSocial.objects.all()
    
    def filter_by_id(self) -> Optional[ObraSocial]:
        return ObraSocial.objects.filter(id=id).first()
    
    def get_by_id(self, id: int) -> Optional[ObraSocial]:
        try:
            obra_social = ObraSocial.objects.get(id=id)
        except:
            obra_social = None
        return obra_social
    
    def delete(self, obra_social: ObraSocial):
        return obra_social.delete()
    
    def create(
        self,
        nombre: str,
        descripcion: str,
    ):
        return ObraSocial.objects.create(
            nombre=nombre,
            descripcion=descripcion,
        )