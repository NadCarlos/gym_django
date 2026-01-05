from typing import List, Optional

from django.contrib.auth.models import User
from rehabilitacion.models import Derivador


class DerivadorRepository:

    def filter_by_id(self, id) -> Optional[Derivador]:
        return Derivador.objects.filter(id=id).first()
    
    def get_by_name(self, nombre: str) -> List[Derivador]:
            return Derivador.objects.get(
                nombre=nombre
            )
    
    def create(
        self,
        id_usuario: User,
        nombre: str,
    ):
        return Derivador.objects.create(
            id_usuario=id_usuario,
            nombre=nombre,
        )