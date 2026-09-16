from django.db import migrations, models

import utils.validators


class Migration(migrations.Migration):
    dependencies = [
        ("finanzas", "0010_factura_id_paciente"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="beneficiario",
                    name="momento_de_carga",
                    field=models.DateTimeField(
                        auto_now_add=True,
                        validators=[utils.validators.validate_date_not_before_1900],
                    ),
                ),
                migrations.AlterField(
                    model_name="factura",
                    name="fecha",
                    field=models.DateField(
                        validators=[utils.validators.validate_date_not_before_1900],
                        verbose_name="fecha",
                    ),
                ),
                migrations.AlterField(
                    model_name="ordenpago",
                    name="fecha",
                    field=models.DateField(
                        validators=[utils.validators.validate_date_not_before_1900],
                        verbose_name="fecha",
                    ),
                ),
                migrations.AlterField(
                    model_name="ordenpago",
                    name="momento_de_carga",
                    field=models.DateTimeField(
                        auto_now_add=True,
                        validators=[utils.validators.validate_date_not_before_1900],
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
