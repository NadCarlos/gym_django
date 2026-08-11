from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from administracion.models import (
    Area,
    EstadoCivil,
    Localidad,
    ObraSocial,
    Paciente,
    PacienteArea,
    Pais,
    Prestacion,
    PrestacionPaciente,
    Provincia,
    Sexo,
)
from administracion.repositories.paciente import PacienteRepository


class PatientExportQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="patient-export")
        pais = Pais.objects.create(nombre="Argentina")
        provincia = Provincia.objects.create(nombre="Cordoba", pais=pais)
        localidad = Localidad.objects.create(nombre="Rio Cuarto", provincia=provincia)
        obra_social = ObraSocial.objects.create(nombre="Particular")
        estado_civil = EstadoCivil.objects.create(nombre="Soltero")
        sexo = Sexo.objects.create(nombre="Masculino")
        cls.paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Exportacion",
            numero_dni="11223344",
            fecha_nacimiento=date(1990, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_obra_social=obra_social,
            id_estado_civil=estado_civil,
            id_sexo=sexo,
        )
        cls.area = Area.objects.create(nombre="Gimnasio")
        PacienteArea.objects.create(
            id_paciente=cls.paciente,
            id_area=cls.area,
            id_usuario=cls.user,
        )
        prestacion = Prestacion.objects.create(nombre="Kinesiologia")
        PrestacionPaciente.objects.create(
            fecha_inicio=date(2026, 1, 1),
            id_prestacion=prestacion,
            id_paciente=cls.paciente,
            id_obra_social=obra_social,
        )

    def test_export_query_preloads_display_fields_and_service_flag(self):
        with self.assertNumQueries(1):
            pacientes = list(
                PacienteRepository().filter_pacientes_area_for_export(
                    state=True,
                    id_area=self.area.id,
                )
            )
            [
                (
                    paciente.id_obra_social.nombre,
                    paciente.id_estado_civil.nombre,
                    paciente.id_localidad.nombre,
                    paciente.id_sexo.nombre,
                    paciente.tiene_prestacion_activa,
                )
                for paciente in pacientes
            ]
