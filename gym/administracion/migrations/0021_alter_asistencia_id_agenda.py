# Generated by Django 4.1.12 on 2024-11-27 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("administracion", "0020_asistencia_id_agenda"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asistencia",
            name="id_agenda",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="agenda",
                to="administracion.agenda",
            ),
        ),
    ]