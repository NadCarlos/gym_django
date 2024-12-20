# Generated by Django 4.1.12 on 2024-11-04 11:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("administracion", "0017_alter_paciente_numero_dni_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=50, verbose_name="Nombre")),
            ],
        ),
        migrations.CreateModel(
            name="Agenda",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha", models.DateField(verbose_name="Fecha")),
                ("hora_inicio", models.TimeField(verbose_name="Hora de Inicio")),
                ("hora_fin", models.TimeField(verbose_name="Hora de Fin")),
                (
                    "tiempo",
                    models.DecimalField(
                        decimal_places=0, max_digits=10, verbose_name="tiempo"
                    ),
                ),
                ("momento_de_carga", models.DateTimeField(auto_now_add=True)),
                ("activo", models.BooleanField(default=1)),
                (
                    "id_dia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="dia_agenda",
                        to="administracion.dia",
                    ),
                ),
                (
                    "id_prestacion_paciente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="prestacion_paciente_agenda",
                        to="administracion.prestacionpaciente",
                    ),
                ),
                (
                    "id_profesional_tratamiento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="profesional_tratamiento_agenda",
                        to="administracion.profesionaltratamiento",
                    ),
                ),
                (
                    "id_usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="usuario_agenda",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
