from datetime import date, time
from types import SimpleNamespace
from uuid import uuid4

from django.db import OperationalError
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase

from administracion.models import (
    Area,
    EstadoCivil,
    Localidad,
    ObraSocial,
    Paciente,
    PacienteArea,
    Pais,
    Profesional,
    Provincia,
    Sexo,
    Tratamiento,
)
from administracion.repositories.paciente import PacienteRepository
from administracion.views.agenda import AgendaDelete
from administracion.views.pacientes import PacienteDelete
from rehabilitacion.models import Turno
from rehabilitacion.repositories.turno import TurnoRepository
from rehabilitacion.views.agenda import AgendaRehabDelete
from rehabilitacion.views.pacitentes_fisiatria import PacienteFisiatriaDelete
from rehabilitacion.views.pacientes_rehab import PacienteRehabDelete
from rehabilitacion.views.turno import TurnoDelete


class WriteEndpointMethodTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_superuser=True)

    def assert_get_not_allowed(self, view_class, **view_kwargs):
        request = self.factory.get("/")
        request.user = self.user

        response = view_class.as_view()(request, id=1, **view_kwargs)

        self.assertEqual(response.status_code, 405)

    def test_turno_delete_rejects_get(self):
        self.assert_get_not_allowed(TurnoDelete)

    def test_agenda_delete_rejects_get(self):
        self.assert_get_not_allowed(AgendaRehabDelete)

    def test_rehab_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteRehabDelete)

    def test_fisiatria_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteFisiatriaDelete)

    def test_gym_agenda_delete_rejects_get(self):
        self.assert_get_not_allowed(AgendaDelete)

    def test_gym_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteDelete)


class LockErrorMiddlewareTests(SimpleTestCase):
    def setUp(self):
        try:
            from gym.middleware import WriteDatabaseInstrumentationMiddleware
        except ImportError as exc:
            self.fail(f"No se pudo importar el middleware de escrituras: {exc}")

        self.middleware_class = WriteDatabaseInstrumentationMiddleware
        self.factory = RequestFactory()

    def test_lock_wait_timeout_returns_retryable_503(self):
        request = self.factory.post("/rehabilitacion/turnos/create/")
        request.user = SimpleNamespace(
            is_authenticated=True,
            pk=7,
            get_username=lambda: "operador",
        )
        middleware = self.middleware_class(lambda request: HttpResponse())

        response = middleware.process_exception(
            request,
            OperationalError(1205, "Lock wait timeout exceeded"),
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response["Retry-After"], "1")

    def test_deadlock_returns_retryable_503(self):
        request = self.factory.post("/rehabilitacion/turnos/update/1/")
        request.user = SimpleNamespace(
            is_authenticated=True,
            pk=7,
            get_username=lambda: "operador",
        )
        middleware = self.middleware_class(lambda request: HttpResponse())

        response = middleware.process_exception(
            request,
            OperationalError(1213, "Deadlock found"),
        )

        self.assertEqual(response.status_code, 503)


class CriticalWriteIdempotencyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User

        cls.user = User.objects.create_user(username="writer", password="test")
        pais = Pais.objects.create(nombre="Argentina")
        provincia = Provincia.objects.create(nombre="Cordoba", pais=pais)
        localidad = Localidad.objects.create(nombre="Rio Cuarto", provincia=provincia)
        obra_social = ObraSocial.objects.create(nombre="Particular")
        estado_civil = EstadoCivil.objects.create(nombre="Soltero")
        sexo = Sexo.objects.create(nombre="Masculino")
        cls.paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Prueba",
            numero_dni="12345678",
            fecha_nacimiento=date(1990, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_obra_social=obra_social,
            id_estado_civil=estado_civil,
            id_sexo=sexo,
        )
        cls.profesional = Profesional.objects.create(
            nombre="Profesional",
            apellido="Prueba",
            numero_dni="87654321",
            matricula="MP-1",
            fecha_nacimiento=date(1980, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_sexo=sexo,
        )
        cls.tratamiento = Tratamiento.objects.create(nombre="Kinesiologia")
        cls.area = Area.objects.create(nombre="Rehabilitacion")

    def test_repeated_request_token_creates_one_turno(self):
        token = uuid4()
        repository = TurnoRepository()
        values = {
            "paciente": self.paciente,
            "profesional": self.profesional,
            "tratamiento": self.tratamiento,
            "fecha": date(2026, 8, 10),
            "hora": time(9, 0),
            "motivo": "CONTROL",
            "request_token": token,
        }

        first = repository.create(**values)
        second = repository.create(**values)

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Turno.objects.filter(request_token=token).count(), 1)

    def test_turno_has_query_indexes_for_profesional_and_paciente(self):
        index_names = {index.name for index in Turno._meta.indexes}

        self.assertIn("turno_prof_fecha_idx", index_names)
        self.assertIn("turno_pac_fecha_idx", index_names)

    def test_repeated_patient_creation_reuses_dni_and_area(self):
        repository = PacienteRepository()
        values = {
            "id_area": self.area,
            "id_usuario": self.user,
            "nombre": "OTRO",
            "apellido": "PACIENTE",
            "numero_dni": "11112222",
            "fecha_nacimiento": date(1991, 2, 2),
            "id_obra_social": self.paciente.id_obra_social,
            "id_estado_civil": self.paciente.id_estado_civil,
            "id_sexo": self.paciente.id_sexo,
            "id_localidad": self.paciente.id_localidad,
        }

        first, first_area_created = repository.create_in_area(**values)
        second, second_area_created = repository.create_in_area(**values)

        self.assertTrue(first_area_created)
        self.assertFalse(second_area_created)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Paciente.objects.filter(numero_dni="11112222").count(), 1)
        self.assertEqual(
            PacienteArea.objects.filter(
                id_paciente=first,
                id_area=self.area,
            ).count(),
            1,
        )
