from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administracion', '0032_agenda_agenda_pac_dia_idx_agenda_agenda_prof_dia_idx_and_more'),
        ('rehabilitacion', '0037_alter_agendarehab_tiempo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisponibilidadProfesionalRehab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de Fin')),
                ('fecha_inicio', models.DateField(verbose_name='Inicio de disponibilidad')),
                ('fecha_fin', models.DateField(blank=True, null=True, verbose_name='Fin de disponibilidad')),
                ('momento_de_carga', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=1)),
                ('id_dia', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='disponibilidades_profesional_rehab', to='administracion.dia')),
                ('id_profesional_area', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='disponibilidades_rehab', to='administracion.profesionalarea')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='usuario_disponibilidad_profesional_rehab', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='disponibilidadprofesionalrehab',
            index=models.Index(fields=['id_profesional_area', 'activo', 'id_dia', 'hora_inicio'], name='disp_rehab_prof_dia_idx'),
        ),
    ]
