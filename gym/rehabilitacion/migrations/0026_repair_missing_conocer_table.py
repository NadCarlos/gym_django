from django.db import migrations


def create_conocer_table_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    table_name = "rehabilitacion_conocer"

    if table_name not in connection.introspection.table_names():
        Conocer = apps.get_model("rehabilitacion", "Conocer")
        schema_editor.create_model(Conocer)

    Conocer = apps.get_model("rehabilitacion", "Conocer")
    if not Conocer.objects.filter(pk=1).exists():
        Conocer.objects.create(id=1, nombre="SIN DEFINIR", activo=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("rehabilitacion", "0025_alter_pacienterehabilitacion_id_conocer"),
    ]

    operations = [
        migrations.RunPython(create_conocer_table_if_missing, noop_reverse),
    ]
