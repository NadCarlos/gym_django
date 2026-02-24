from typing import List, Optional

from rehabilitacion.models import Archivo, Informe


class ArchivoRepository:

    def get_all(self) -> List[Archivo]:
        return Archivo.objects.all()

    def get_by_id(self, id: int) -> Optional[Archivo]:
        return Archivo.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Archivo]:
        return Archivo.objects.filter(id=id).first()
    
    def filter_by_informe_id(self, informe_id) -> Optional[Archivo]:
        return Archivo.objects.filter(id_informe=informe_id)
    
    def create(
        self,
        archivo: str,
        id_informe: Informe,
        ):
        return Archivo.objects.create(
            archivo=archivo,
            id_informe=id_informe,
        )
    
    def delete(self, archivo: Archivo):
        return archivo.delete()