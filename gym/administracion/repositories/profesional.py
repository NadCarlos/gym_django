from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Profesional, Sexo, Localidad


class PacienteRepository:

    def get_all(self) -> List[Profesional]:
        return Profesional.objects.all().order_by('apellido').values()
    
    def filter_by_id(self) -> Optional[Profesional]:
        return Profesional.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Profesional]:
        return Profesional.objects.filter(
            activo=True
        ).order_by('apellido')

    def get_by_id(self, id: int) -> Optional[Profesional]:
        try:
            profesional = Profesional.objects.get(id=id)
        except:
            profesional = None
        return profesional 
    
    def get_by_dni(self, numero_dni: int) -> Optional[Profesional]:
        try:
            profesional = Profesional.objects.get(numero_dni=numero_dni)
        except:
            profesional = None
        return profesional
    
    def delete(self, profesional: Profesional):
        return profesional.delete()
    
    def delete_by_activo(self, profesional: Profesional):
        profesional.activo=False
        profesional.save()

    def create(
        self,
        id_usuario: User,
        nombre: str,
        apellido: str,
        numero_dni: str,
        matricula: str,
        fecha_nacimiento: str,
        id_localidad: Localidad,
        id_sexo: Sexo,
        direccion: Optional[str] = None,
        celular: Optional[str] = None,
    ):
        return Profesional.objects.create(
            id_usuario=id_usuario,
            nombre=nombre,
            apellido=apellido,
            numero_dni=numero_dni,
            matricula=matricula,
            fecha_nacimiento=fecha_nacimiento,
            id_localidad=id_localidad,
            id_sexo=id_sexo,
            direccion=direccion,
            celular=celular,
        )
    
    def update(
        self, 
        profesional: Profesional,
        nombre: str,
        apellido: str,
        numero_dni: str,
        matricula: str,
        direccion: str,
        celular: str,
        fecha_nacimiento: str,
        sexo: Sexo,
        localidad: Localidad,
    ) -> Profesional:

        profesional.nombre = nombre
        profesional.apellido = apellido
        profesional.numero_dni = numero_dni
        profesional.matricula = matricula
        profesional.direccion = direccion
        profesional.celular = celular
        profesional.fecha_nacimiento = fecha_nacimiento
        profesional.id_sexo = sexo
        profesional.id_localidad = localidad

        profesional.save()