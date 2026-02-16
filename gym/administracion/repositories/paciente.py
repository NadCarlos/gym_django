from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Paciente, ObraSocial, EstadoCivil, Sexo, Localidad, PacienteArea


class PacienteRepository:

    def get_all(self) -> List[Paciente]:
        return Paciente.objects.all().order_by('apellido').values()
    
    def get_all_2(self) -> List[Paciente]:
        return Paciente.objects.all().order_by('apellido')
    
    def filter_by_id(self) -> Optional[Paciente]:
        return Paciente.objects.filter(id=id).first()
    
    def filter_by_dni(self, numero_dni, id_area) -> Optional[Paciente]:
        ids_pacientes = PacienteArea.objects.filter(id_area=id_area).values_list('id_paciente', flat=True)
        return Paciente.objects.filter(id__in=ids_pacientes).filter(numero_dni=numero_dni).first()
    
    def filter_by_activo(self, state) -> List[Paciente]:
        return Paciente.objects.filter(
            activo=state
        ).order_by('apellido')
    
    def filter_pacientes_area(self, state, id_area) -> List[Paciente]:
        # Obtener IDs de pacientes relacionados con id_area = 1
        ids_pacientes = PacienteArea.objects.filter(id_area=id_area).values_list('id_paciente', flat=True)

        # Obtener el queryset de pacientes
        return Paciente.objects.filter(id__in=ids_pacientes).filter(activo=state).order_by('apellido')
    
    def dni_list_segun_area(self, id_area):
        ids_pacientes = PacienteArea.objects.filter(id_area=id_area).values_list('id_paciente', flat=True)
        pacientes = Paciente.objects.filter(id__in=ids_pacientes).order_by('apellido')
        return list(pacientes.values_list('numero_dni', flat=True))

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

    def reactivate(self, paciente: Paciente):
        paciente.activo=True
        paciente.save()

    def create(
        self,
        id_usuario: User,
        nombre: str,
        apellido: str,
        numero_dni: str,
        fecha_nacimiento: str,
        id_obra_social: ObraSocial,
        id_estado_civil: EstadoCivil,
        id_sexo: Sexo,
        id_localidad: Localidad,
        direccion: Optional[str] = None,
        celular: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        observaciones: Optional[str] = None,
    ):
        return Paciente.objects.create(
            id_usuario=id_usuario,
            nombre=nombre,
            apellido=apellido,
            numero_dni=numero_dni,
            fecha_nacimiento=fecha_nacimiento,
            id_obra_social=id_obra_social,
            id_estado_civil=id_estado_civil,
            id_sexo=id_sexo,
            id_localidad=id_localidad,
            direccion=direccion,
            celular=celular,
            email=email,
            telefono=telefono,
            observaciones=observaciones,
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
        email: str,
        observaciones: str,
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
        paciente.email = email
        paciente.observaciones=observaciones
        paciente.fecha_nacimiento = fecha_nacimiento
        paciente.id_obra_social = obra_social
        paciente.id_estado_civil = estado_civil
        paciente.id_sexo = sexo
        paciente.id_localidad = localidad

        paciente.save()


    def update_o_soc_e_civ(
        self, 
        paciente: Paciente,
        obra_social: ObraSocial,
        estado_civil: EstadoCivil,
    ) -> Paciente:

        paciente.id_obra_social = obra_social
        paciente.id_estado_civil = estado_civil

        paciente.save()