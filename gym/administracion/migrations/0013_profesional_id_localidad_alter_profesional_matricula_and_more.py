# Generated by Django 4.1.12 on 2024-10-08 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "administracion",
            "0012_rename_profecionaltratamiento_profesionaltratamiento_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="profesional",
            name="id_localidad",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="localidad_prof",
                to="administracion.localidad",
            ),
        ),
        migrations.AlterField(
            model_name="profesional",
            name="matricula",
            field=models.CharField(default=5, max_length=20, verbose_name="Matricula"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="profesionaltratamiento",
            name="fecha_inicio",
            field=models.DateField(verbose_name="Inicio del Tratamiento"),
        ),
    ]
