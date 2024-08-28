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
    
    def delete_by_activo(self, obra_social: ObraSocial):
        obra_social.activo=False
        obra_social.save()
    
    def create(
        self,
        nombre: str,
        descripcion: str,
    ):
        return ObraSocial.objects.create(
            nombre=nombre,
            descripcion=descripcion,
        )
    
    def update(
        self, 
        obra_social: ObraSocial,
        nombre: str,
        descripcion: str,
    ) -> ObraSocial:

        obra_social.nombre = nombre
        obra_social.descripcion = descripcion

        obra_social.save()