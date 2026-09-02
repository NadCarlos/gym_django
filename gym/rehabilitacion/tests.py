from datetime import date, time
import os
import threading
from time import monotonic
from unittest.mock import patch
from types import SimpleNamespace
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import OperationalError
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from administracion.models import (
    Area,
    Dia,
    EstadoCivil,
    Localidad,
    ObraSocial,
    Paciente,
    PacienteArea,
    Pais,
    Profesional,
    ProfesionalArea,
    Provincia,
    Sexo,
    Tratamiento,
)
from administracion.repositories.paciente import PacienteRepository
from administracion.views.agenda import AgendaDelete
from administracion.views.pacientes import PacienteDelete, PacienteRedirectFromExistent
from rehabilitacion.models import (
    Alta,
    AltaEtiologico,
    AltaFuncional,
    AltaTipoDiscapacidad,
    Conocer,
    Derivador,
    DiagnosticoEtiologico,
    DiagnosticoFuncional,
    EstadoCertificado,
    PacienteRehabilitacion,
    PacienteRehabilitacionSituacion,
    Situacion,
    TipoDiscapacidad,
    Turno,
    DisponibilidadProfesionalRehab,
)
from rehabilitacion.repositories.disponibilidad_profesional_rehab import DisponibilidadProfesionalRehabRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository
from rehabilitacion.repositories.alta import AltaRepository
from rehabilitacion.repositories.situacion import PacienteRehabilitacionSituacionRepository
from rehabilitacion.repositories.turno import TurnoRepository
from rehabilitacion.views.agenda import (
    AgendaPacienteRehabUpdate,
    AgendaProfesionalRehab,
    AgendaProfesionalRehabToPDF,
    AgendaRehabDelete,
    DisponibilidadProfesionalRehabDelete,
)
from rehabilitacion.views.pacitentes_fisiatria import (
    PacienteFisiatriaDelete,
    PacienteFisiatriaRedirectFromExistent,
)
from rehabilitacion.views.pacientes_rehab import (
    PacienteRehabDelete,
    PacienteRehabRedirectFromExistent,
    PacientesRehabList,
)
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

    def test_disponibilidad_delete_rejects_get(self):
        self.assert_get_not_allowed(DisponibilidadProfesionalRehabDelete)

    def test_rehab_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteRehabDelete)

    def test_fisiatria_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteFisiatriaDelete)

    def test_gym_agenda_delete_rejects_get(self):
        self.assert_get_not_allowed(AgendaDelete)

    def test_gym_patient_delete_rejects_get(self):
        self.assert_get_not_allowed(PacienteDelete)

    def assert_redirect_from_existent_accepts_post(
        self,
        view_class,
        repo_path,
        expected_url,
    ):
        request = self.factory.post("/", {"dni": "12345678"})
        request.user = self.user

        with patch(repo_path, return_value=SimpleNamespace(id=42)) as get_by_dni:
            response = view_class.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
        get_by_dni.assert_called_once_with(numero_dni=12345678)

    def test_gym_patient_redirect_from_existent_accepts_post(self):
        self.assert_redirect_from_existent_accepts_post(
            PacienteRedirectFromExistent,
            "administracion.views.pacientes.pacienteRepo.get_by_dni",
            "/administracion/42/paciente_detail/",
        )

    def test_rehab_patient_redirect_from_existent_accepts_post(self):
        self.assert_redirect_from_existent_accepts_post(
            PacienteRehabRedirectFromExistent,
            "rehabilitacion.views.pacientes_rehab.pacienteRepo.get_by_dni",
            "/rehabilitacion/pacientes/detail/42",
        )

    def test_fisiatria_patient_redirect_from_existent_accepts_post(self):
        self.assert_redirect_from_existent_accepts_post(
            PacienteFisiatriaRedirectFromExistent,
            "rehabilitacion.views.pacitentes_fisiatria.pacienteRepo.get_by_dni",
            "/rehabilitacion/pacientes/fisiatria/detail/42",
        )


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


class DisponibilidadProfesionalRehabRepositoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="rehab", password="test")
        pais = Pais.objects.create(nombre="Argentina")
        provincia = Provincia.objects.create(nombre="Cordoba", pais=pais)
        localidad = Localidad.objects.create(nombre="Rio Cuarto", provincia=provincia)
        obra_social = ObraSocial.objects.create(nombre="Particular")
        estado_civil = EstadoCivil.objects.create(nombre="Soltero")
        sexo = Sexo.objects.create(nombre="Femenino")
        cls.area = Area.objects.create(nombre="Rehabilitacion")
        cls.dia_lunes = Dia.objects.create(nombre="Lunes")
        cls.dia_martes = Dia.objects.create(nombre="Martes")
        cls.paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Agenda",
            numero_dni="22333444",
            fecha_nacimiento=date(1992, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_obra_social=obra_social,
            id_estado_civil=estado_civil,
            id_sexo=sexo,
        )
        cls.profesional = Profesional.objects.create(
            nombre="Profesional",
            apellido="Agenda",
            numero_dni="33444555",
            matricula="MP-2",
            fecha_nacimiento=date(1982, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_sexo=sexo,
        )
        cls.tratamiento = Tratamiento.objects.create(nombre="Terapia")
        cls.paciente_area = PacienteArea.objects.create(
            id_area=cls.area,
            id_paciente=cls.paciente,
            id_usuario=cls.user,
        )
        cls.profesional_area = ProfesionalArea.objects.create(
            id_area=cls.area,
            id_profesional=cls.profesional,
            id_usuario=cls.user,
        )

    def setUp(self):
        self.repository = DisponibilidadProfesionalRehabRepository()

    def test_bypasses_disponibilidad_when_profesional_has_no_records(self):
        permitido = self.repository.is_agenda_within_disponibilidad(
            id_profesional_area=self.profesional_area.id,
            id_dia=self.dia_lunes,
            fecha=date(2026, 9, 7),
            hora_inicio=time(7, 0),
            hora_fin=time(8, 0),
        )

        self.assertTrue(permitido)

    def test_accepts_agenda_fully_inside_existing_disponibilidad(self):
        self.create_disponibilidad(self.dia_lunes, time(8, 0), time(12, 0))

        permitido = self.repository.is_agenda_within_disponibilidad(
            id_profesional_area=self.profesional_area.id,
            id_dia=self.dia_lunes,
            fecha=date(2026, 9, 7),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )

        self.assertTrue(permitido)

    def test_rejects_agenda_outside_existing_disponibilidad(self):
        self.create_disponibilidad(self.dia_lunes, time(8, 0), time(12, 0))

        permitido = self.repository.is_agenda_within_disponibilidad(
            id_profesional_area=self.profesional_area.id,
            id_dia=self.dia_lunes,
            fecha=date(2026, 9, 7),
            hora_inicio=time(11, 30),
            hora_fin=time(12, 30),
        )

        self.assertFalse(permitido)

    def create_disponibilidad(self, dia, hora_inicio, hora_fin):
        return DisponibilidadProfesionalRehab.objects.create(
            id_profesional_area=self.profesional_area,
            id_dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            fecha_inicio=date(2026, 1, 1),
            id_usuario=self.user,
        )
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Paciente.objects.filter(numero_dni="11112222").count(), 1)
        self.assertEqual(
            PacienteArea.objects.filter(
                id_paciente=first,
                id_area=self.area,
            ).count(),
            1,
        )


    def test_patient_area_list_preloads_related_display_fields(self):
        PacienteArea.objects.create(
            id_paciente=self.paciente,
            id_area=self.area,
            id_usuario=self.user,
        )

        with self.assertNumQueries(1):
            pacientes = list(
                PacienteRepository().filter_pacientes_area(state=True, id_area=self.area.id)
            )
            [(paciente.id_obra_social, paciente.id_sexo.nombre) for paciente in pacientes]


class RequestTimingMiddlewareTests(SimpleTestCase):
    @override_settings(
        REQUEST_INSTRUMENTATION_ENABLED=True,
        SLOW_REQUEST_LOG_MS=0,
        SLOW_REQUEST_WATCHDOG_ENABLED=False,
    )
    def test_get_request_is_logged_when_slow(self):
        from gym.middleware import WriteDatabaseInstrumentationMiddleware

        request = RequestFactory().get("/rehabilitacion/")
        middleware = WriteDatabaseInstrumentationMiddleware(lambda request: HttpResponse())

        with self.assertLogs("cermed.request_timing", level="WARNING") as logs:
            response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("[SLOW-REQUEST] finish", logs.output[0])
        self.assertIn("method=GET", logs.output[0])

    def test_watchdog_logs_current_thread_stack_once(self):
        from gym.slow_requests import ActiveRequestRegistry

        registry = ActiveRequestRegistry()
        registry._active["request-1"] = {
            "pid": os.getpid(),
            "thread_id": threading.get_ident(),
            "method": "GET",
            "path": "/rehabilitacion/",
            "view": "rehabilitacion.views.inicio.index.IndexView",
            "started_at": monotonic() - 11,
            "stack_after_ms": 10000,
            "stack_logged": False,
        }

        with self.assertLogs("cermed.request_timing", level="WARNING") as logs:
            registry.emit_overdue_stacks()
            registry.emit_overdue_stacks()

        self.assertEqual(len(logs.output), 1)
        self.assertIn("request_id=request-1", logs.output[0])
        self.assertTrue(registry._active["request-1"]["stack_logged"])


class AgendaPacienteRehabUpdateTests(SimpleTestCase):
    def test_post_without_session_return_path_redirects_to_patient_agenda(self):
        agenda = SimpleNamespace(
            id_paciente_area=SimpleNamespace(id_paciente_id=42),
        )
        form = SimpleNamespace(
            is_valid=lambda: True,
            cleaned_data={
                "hora_inicio": time(9, 0),
                "hora_fin": time(10, 0),
                "id_dia": SimpleNamespace(id=1),
                "observaciones": "control",
            },
        )
        request = SimpleNamespace(
            POST={"id_tratamiento": "1", "profesional": "2"},
            session={},
        )

        with patch("rehabilitacion.views.agenda.AgendaRehabUpdateForm", return_value=form), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.get_by_id", return_value=agenda), \
             patch("rehabilitacion.views.agenda.tratamientoRepo.filter_by_id", return_value=SimpleNamespace(id=1)), \
             patch("rehabilitacion.views.agenda.profesionalRepo.filter_by_id", return_value=SimpleNamespace(id=2)), \
             patch("rehabilitacion.views.agenda.profesionalAreaRepo.filter_by_profesional_id", return_value=SimpleNamespace(id=3)), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.update"):
            response = AgendaPacienteRehabUpdate().post(request, id=11)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/rehabilitacion/agenda_paciente_rehab/42")

    def test_post_without_profesional_renders_error_instead_of_500(self):
        agenda = SimpleNamespace(
            id_paciente_area=SimpleNamespace(
                id_paciente=SimpleNamespace(nombre="Paciente", apellido="Test"),
                id_paciente_id=42,
            ),
            id_profesional_area=SimpleNamespace(id_profesional=SimpleNamespace(id=2)),
            id_tratamiento_rehab=SimpleNamespace(id=1),
        )
        form = SimpleNamespace(
            is_valid=lambda: True,
            cleaned_data={
                "hora_inicio": time(9, 0),
                "hora_fin": time(10, 0),
                "id_dia": SimpleNamespace(id=1),
                "observaciones": "control",
            },
        )
        request = SimpleNamespace(
            POST={},
            session={},
        )

        with patch("rehabilitacion.views.agenda.AgendaRehabUpdateForm", return_value=form), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.get_by_id", return_value=agenda), \
             patch("rehabilitacion.views.agenda.tratamientoRepo.filter_by_id", return_value=None), \
             patch("rehabilitacion.views.agenda.profesionalRepo.filter_by_id", return_value=None), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.update") as update_mock, \
             patch("rehabilitacion.views.agenda.render", return_value=HttpResponse("error")) as render_mock:
            response = AgendaPacienteRehabUpdate().post(request, id=11)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(update_mock.called)
        context = render_mock.call_args[0][2]
        self.assertEqual(
            context["error_message"],
            'Debe seleccionar un tratamiento y un profesional de Rehabilitación.',
        )

    def test_post_with_invalid_form_renders_error_instead_of_500(self):
        agenda = SimpleNamespace(
            id_paciente_area=SimpleNamespace(
                id_paciente=SimpleNamespace(nombre="Paciente", apellido="Test"),
                id_paciente_id=42,
            ),
            id_profesional_area=SimpleNamespace(id_profesional=SimpleNamespace(id=2)),
            id_tratamiento_rehab=SimpleNamespace(id=1),
        )
        form = SimpleNamespace(
            is_valid=lambda: False,
            cleaned_data={},
        )
        request = SimpleNamespace(
            POST={},
            session={},
        )

        with patch("rehabilitacion.views.agenda.AgendaRehabUpdateForm", return_value=form), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.get_by_id", return_value=agenda), \
             patch("rehabilitacion.views.agenda.agendaRehabRepo.update") as update_mock, \
             patch("rehabilitacion.views.agenda.render", return_value=HttpResponse("error")) as render_mock:
            response = AgendaPacienteRehabUpdate().post(request, id=11)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(update_mock.called)
        context = render_mock.call_args[0][2]
        self.assertEqual(context["error_message"], None)


class AgendaProfesionalRehabTests(SimpleTestCase):
    def setUp(self):
        self.request = SimpleNamespace(
            path="/rehabilitacion/profesionales/agenda/3/",
            session={},
        )

    def test_get_without_profesional_redirects_to_error(self):
        with patch("rehabilitacion.views.agenda.profesionalRepo.get_by_id", return_value=None):
            response = AgendaProfesionalRehab().get(self.request, id=99)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/error/")

    def test_get_without_profesional_area_redirects_to_error(self):
        profesional = SimpleNamespace(id=3)

        with patch("rehabilitacion.views.agenda.profesionalRepo.get_by_id", return_value=profesional), \
             patch("rehabilitacion.views.agenda.profesionalAreaRepo.filter_by_profesional_id", return_value=None):
            response = AgendaProfesionalRehab().get(self.request, id=3)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/error/")

    def test_pdf_without_profesional_redirects_to_error(self):
        with patch("rehabilitacion.views.agenda.profesionalRepo.get_by_id", return_value=None):
            response = AgendaProfesionalRehabToPDF().get(self.request, id=99)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/error/")

    def test_pdf_without_profesional_area_redirects_to_error(self):
        profesional = SimpleNamespace(id=3)

        with patch("rehabilitacion.views.agenda.profesionalRepo.get_by_id", return_value=profesional), \
             patch("rehabilitacion.views.agenda.profesionalAreaRepo.filter_by_profesional_id", return_value=None):
            response = AgendaProfesionalRehabToPDF().get(self.request, id=3)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/error/")



class RehabPatientDetailQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User

        cls.user = User.objects.create_user(username="rehab-detail-query")
        pais = Pais.objects.create(nombre="Argentina")
        provincia = Provincia.objects.create(nombre="Cordoba", pais=pais)
        localidad = Localidad.objects.create(nombre="Rio Cuarto", provincia=provincia)
        obra_social = ObraSocial.objects.create(nombre="Particular")
        estado_civil = EstadoCivil.objects.create(nombre="Soltero")
        sexo = Sexo.objects.create(nombre="Masculino")
        paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Detalle",
            numero_dni="55667788",
            fecha_nacimiento=date(1990, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_obra_social=obra_social,
            id_estado_civil=estado_civil,
            id_sexo=sexo,
        )
        area = Area.objects.create(nombre="Rehabilitacion")
        paciente_area = PacienteArea.objects.create(
            id_paciente=paciente,
            id_area=area,
            id_usuario=cls.user,
        )
        rehabilitacion = PacienteRehabilitacion.objects.create(
            id_paciente_area=paciente_area,
            id_estado_certificado=EstadoCertificado.objects.create(nombre="SI"),
            id_derivador=Derivador.objects.create(
                nombre="Derivador",
                id_usuario=cls.user,
            ),
            id_obra_social=obra_social,
            id_conocer=Conocer.objects.create(nombre="Redes"),
            id_usuario=cls.user,
        )
        alta = Alta.objects.create(
            fecha=date(2026, 1, 1),
            id_paciente_rehabilitacion=rehabilitacion,
        )
        tipo = TipoDiscapacidad.objects.create(nombre="Motora")
        etiologico = DiagnosticoEtiologico.objects.create(nombre="Origen")
        funcional = DiagnosticoFuncional.objects.create(nombre="Funcion")
        AltaTipoDiscapacidad.objects.create(
            id_alta=alta,
            id_tipo_discapacidad=tipo,
            id_usuario=cls.user,
        )
        AltaEtiologico.objects.create(
            id_alta=alta,
            id_diagnostico_etiologico=etiologico,
            id_usuario=cls.user,
        )
        AltaFuncional.objects.create(
            id_alta=alta,
            id_diagnostico_funcional=funcional,
            id_usuario=cls.user,
        )
        cls.rehabilitacion = rehabilitacion

    def test_detail_prefetches_all_alta_relations_with_constant_queries(self):
        with self.assertNumQueries(4):
            altas = list(
                AltaRepository().filter_for_patient_detail(
                    self.rehabilitacion.id,
                )
            )
            [
                (
                    alta.altas_tipo_discapacidad[0].id_tipo_discapacidad.nombre,
                    alta.altas_etiologicos[0].id_diagnostico_etiologico.nombre,
                    alta.altas_funcionales[0].id_diagnostico_funcional.nombre,
                )
                for alta in altas
            ]


class PacienteRehabilitacionSituacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User

        cls.user = User.objects.create_user(username="situacion-rehab")
        pais = Pais.objects.create(nombre="Argentina")
        provincia = Provincia.objects.create(nombre="Cordoba", pais=pais)
        localidad = Localidad.objects.create(nombre="Rio Cuarto", provincia=provincia)
        cls.obra_social = ObraSocial.objects.create(nombre="Particular")
        estado_civil = EstadoCivil.objects.create(nombre="Soltero")
        sexo = Sexo.objects.create(nombre="Masculino")
        paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Situacion",
            numero_dni="99112233",
            fecha_nacimiento=date(1990, 1, 1),
            id_usuario=cls.user,
            id_localidad=localidad,
            id_obra_social=cls.obra_social,
            id_estado_civil=estado_civil,
            id_sexo=sexo,
        )
        cls.area = Area.objects.create(nombre="Rehabilitacion")
        cls.paciente_area = PacienteArea.objects.create(
            id_paciente=paciente,
            id_area=cls.area,
            id_usuario=cls.user,
        )
        cls.estado_certificado = EstadoCertificado.objects.create(nombre="SI")
        cls.derivador = Derivador.objects.create(
            nombre="Derivador",
            id_usuario=cls.user,
        )
        cls.conocer = Conocer.objects.create(nombre="Redes")

    def create_rehabilitacion(self):
        return PacienteRehabilitacionRepository().create(
            id_paciente_area=self.paciente_area,
            nombre_tutor="NO",
            celular_tutor="",
            hijos=0,
            id_estado_certificado=self.estado_certificado,
            vencimiento_certificado=None,
            fecha_junta=None,
            ven_presupuesto=False,
            vencimiento_presupuesto=None,
            id_derivador=self.derivador,
            puerto_esperanza=False,
            id_obra_social=self.obra_social,
            numero_afiliado="0",
            id_conocer=self.conocer,
            id_usuario=self.user,
            diagnosticoCUD="",
            pre_ingreso=False,
        )

    def test_create_rehabilitacion_creates_initial_situacion(self):
        rehabilitacion = self.create_rehabilitacion()

        situacion = PacienteRehabilitacionSituacion.objects.get(
            idpacienterehabilitacion=rehabilitacion,
        )

        self.assertEqual(situacion.idsituacion_id, 1)
        self.assertEqual(situacion.idsituacion.nombre, "Carga inicial")

    def test_get_ultima_orders_by_fecha_and_id(self):
        rehabilitacion = self.create_rehabilitacion()
        segunda_situacion = Situacion.objects.create(nombre="En tratamiento")
        fecha = timezone.now()
        primera = PacienteRehabilitacionSituacion.objects.create(
            idpacienterehabilitacion=rehabilitacion,
            idsituacion=segunda_situacion,
            fecha=fecha,
        )
        ultima = PacienteRehabilitacionSituacion.objects.create(
            idpacienterehabilitacion=rehabilitacion,
            idsituacion=segunda_situacion,
            fecha=fecha,
            observaciones="Última por id",
        )

        resultado = PacienteRehabilitacionSituacionRepository().get_ultima(
            id_paciente_rehabilitacion=rehabilitacion.id,
        )

        self.assertLess(primera.id, ultima.id)
        self.assertEqual(resultado.id, ultima.id)

    def test_patient_export_queryset_includes_latest_situacion(self):
        rehabilitacion = self.create_rehabilitacion()
        alta_situacion = Situacion.objects.create(nombre="Alta en seguimiento")
        PacienteRehabilitacionSituacion.objects.create(
            idpacienterehabilitacion=rehabilitacion,
            idsituacion=alta_situacion,
            fecha=timezone.now(),
        )

        paciente = (
            PacienteRepository()
            .filter_pacientes_area_for_export(state=True, id_area=self.area.id)
            .get(pk=self.paciente_area.id_paciente_id)
        )

        self.assertEqual(paciente.ultima_situacion, "Alta en seguimiento")

    def test_update_situacion_changes_expediente_fecha_and_observaciones(self):
        rehabilitacion = self.create_rehabilitacion()
        nueva_situacion = Situacion.objects.create(nombre="Pendiente auditoria")
        paciente_situacion = PacienteRehabilitacionSituacion.objects.get(
            idpacienterehabilitacion=rehabilitacion,
        )
        nueva_fecha = timezone.now()

        PacienteRehabilitacionSituacionRepository().update(
            paciente_situacion=paciente_situacion,
            idsituacion=nueva_situacion,
            fecha=nueva_fecha,
            observaciones="Expediente observado",
        )
        paciente_situacion.refresh_from_db()

        self.assertEqual(paciente_situacion.idsituacion, nueva_situacion)
        self.assertEqual(paciente_situacion.fecha, nueva_fecha)
        self.assertEqual(paciente_situacion.observaciones, "Expediente observado")

    def test_delete_situacion_removes_history_item(self):
        rehabilitacion = self.create_rehabilitacion()
        paciente_situacion = PacienteRehabilitacionSituacion.objects.get(
            idpacienterehabilitacion=rehabilitacion,
        )

        PacienteRehabilitacionSituacionRepository().delete(
            paciente_situacion=paciente_situacion,
        )

        self.assertFalse(
            PacienteRehabilitacionSituacion.objects.filter(
                id=paciente_situacion.id,
            ).exists()
        )

    def test_patient_list_queryset_includes_latest_situacion_for_filtering_and_ordering(self):
        rehabilitacion = self.create_rehabilitacion()
        alta_situacion = Situacion.objects.create(nombre="Alta en seguimiento")
        PacienteRehabilitacionSituacion.objects.create(
            idpacienterehabilitacion=rehabilitacion,
            idsituacion=alta_situacion,
            fecha=timezone.now(),
        )

        pacientes = (
            PacienteRepository()
            .filter_pacientes_area_with_ultima_situacion(state=True, id_area=self.area.id)
            .filter(ultima_situacion_id=alta_situacion.pk)
            .order_by("ultima_situacion")
        )

        paciente = pacientes.get(pk=self.paciente_area.id_paciente_id)
        self.assertEqual(paciente.ultima_situacion, "Alta en seguimiento")

    def test_patient_list_rejects_invalid_ordering(self):
        view = PacientesRehabList()
        request = RequestFactory().get("/", {"ordering": "no_existe"})

        self.assertEqual(view.get_ordering(request), "apellido")
