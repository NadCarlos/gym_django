# Generated by Django 4.1.12 on 2024-08-28 14:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administracion", "0004_alter_paciente_id_estado_civil_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="obrasocial",
            name="activo",
            field=models.BooleanField(default=1),
        ),
        migrations.AddField(
            model_name="prestacion",
            name="activo",
            field=models.BooleanField(default=1),
        ),
    ]
