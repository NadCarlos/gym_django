# Generated by Django 4.1.12 on 2024-08-30 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administracion", "0006_paciente_observaciones_alter_obrasocial_descripcion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="obrasocial",
            name="descripcion",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="paciente",
            name="apellido",
            field=models.CharField(max_length=150, verbose_name="Apellido"),
        ),
        migrations.AlterField(
            model_name="paciente",
            name="celular",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Numero Celular"
            ),
        ),
        migrations.AlterField(
            model_name="paciente",
            name="nombre",
            field=models.CharField(max_length=150, verbose_name="Nombre"),
        ),
        migrations.AlterField(
            model_name="paciente",
            name="observaciones",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Obseraciones"
            ),
        ),
        migrations.AlterField(
            model_name="prestacionpaciente",
            name="fecha_fin",
            field=models.DateField(
                blank=True, null=True, verbose_name="Fin de la prestacion"
            ),
        ),
        migrations.AlterField(
            model_name="prestacionpaciente",
            name="fecha_inicio",
            field=models.DateField(verbose_name="Inicio de la prestacion"),
        ),
        migrations.AlterField(
            model_name="prestacionpaciente",
            name="id_obra_social",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=models.SET(1),
                related_name="obra_social_prestacion",
                to="administracion.obrasocial",
            ),
        ),
        migrations.AlterField(
            model_name="prestacionpaciente",
            name="id_prestacion",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=models.SET(1),
                related_name="prestacion",
                to="administracion.prestacion",
            ),
        ),
    ]
