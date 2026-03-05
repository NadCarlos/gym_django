from typing import List, Optional

from rehabilitacion.models import Link, Informe


class LinkRepository:

    def get_all(self) -> List[Link]:
        return Link.objects.all()

    def get_by_id(self, id: int) -> Optional[Link]:
        return Link.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Link]:
        return Link.objects.filter(id=id).first()
    
    def filter_by_informe_id(self, informe_id) -> Optional[Link]:
        return Link.objects.filter(id_informe=informe_id)
    
    def create(
        self,
        nombre: str,
        url: str,
        id_informe: Informe,
        ):
        return Link.objects.create(
            nombre=nombre,
            url=url,
            id_informe=id_informe,
        )
    
    def delete(self, link: Link):
        return link.delete()