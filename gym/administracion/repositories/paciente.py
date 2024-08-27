from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Paciente, ObraSocial, EstadoCivil, Sexo, Localidad


class PacienteRepository:

    def get_all(self) -> List[Paciente]:
        return Paciente.objects.all()
    
    def filter_by_id(self) -> Optional[Paciente]:
        return Paciente.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Paciente]:
        return Paciente.objects.filter(
            activo=True
        )

    def get_by_id(self, id: int) -> Optional[Paciente]:
        try:
            paciente = Paciente.objects.get(id=id)
        except:
            paciente = None
        return paciente 
    
    def get_by_dni(self, numero_dni: int) -> Optional[Paciente]:
        try:
            paciente = Paciente.objects.get(numero_dni=numero_dni)
        except:
            paciente = None
        return paciente
    
    def delete(self, paciente: Paciente):
        return paciente.delete()
    
    def delete_by_activo(self, paciente: Paciente):
        paciente.activo=False
        paciente.save()

    def create(
        self,
        nombre: str,
        apellido: str,
        numero_dni: str,
        direccion: str,
        fecha_nacimiento: str,
        celular: str,
        obraSocial: ObraSocial,
        estadoCivil: EstadoCivil,
        sexo: Sexo,
        localidad: Localidad,
        usuario: User,
        telefono: Optional[str] = None,
    ):
        return Paciente.objects.create(
            nombre=nombre,
            apellido=apellido,
            numero_dni=numero_dni,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            celular=celular,
            id_obra_social=obraSocial,
            id_estado_civil=estadoCivil,
            id_sexo=sexo,
            id_localidad=localidad,
            id_usuario=usuario,
            telefono=telefono,
        )
    
    def update(
        self, 
        paciente: Paciente,
        nombre: str,
        apellido: str,
        numero_dni: str,
        direccion: str,
        telefono: str,
        celular: str,
        fecha_nacimiento: str,
        obra_social: ObraSocial,
        estado_civil: EstadoCivil,
        sexo: Sexo,
        localidad: Localidad,
    ) -> Paciente:

        paciente.nombre = nombre
        paciente.apellido = apellido
        paciente.numero_dni = numero_dni
        paciente.direccion = direccion
        paciente.telefono = telefono
        paciente.celular = celular
        paciente.fecha_nacimiento = fecha_nacimiento
        paciente.id_obra_social = obra_social
        paciente.id_estado_civil = estado_civil
        paciente.id_sexo = sexo
        paciente.id_localidad = localidad

        paciente.save()