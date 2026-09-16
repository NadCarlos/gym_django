from datetime import date

from django import forms
from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
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
from utils.validators import validate_date_not_before_1900


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


class DateFieldValidationTests(TestCase):
    def test_rejects_dates_before_1900(self):
        with self.assertRaises(ValidationError):
            validate_date_not_before_1900(date(1899, 12, 31))

    def test_all_model_date_fields_use_minimum_date_validator(self):
        missing_fields = []

        for model in apps.get_models():
            if model._meta.app_label not in {"administracion", "finanzas", "rehabilitacion"}:
                continue

            for field in model._meta.get_fields():
                if isinstance(field, (models.DateField, models.DateTimeField)):
                    if validate_date_not_before_1900 not in field.validators:
                        missing_fields.append(f"{model.__name__}.{field.name}")

        self.assertEqual(missing_fields, [])

    def test_model_form_shows_validation_error_for_date_before_1900(self):
        class PacienteBirthDateForm(forms.ModelForm):
            class Meta:
                model = Paciente
                fields = ["fecha_nacimiento"]

        form = PacienteBirthDateForm(data={"fecha_nacimiento": "1899-12-31"})

        self.assertFalse(form.is_valid())
        self.assertIn("fecha_nacimiento", form.errors)
