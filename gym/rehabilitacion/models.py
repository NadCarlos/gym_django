from django.db import models
from django.contrib.auth.models import User
import os

from administracion.models import (
    PacienteArea,
    ObraSocial,
    Tratamiento,
    ProfesionalArea,
    Dia,
    Profesional,
    Paciente,
    ProfesionalTratamiento,
)


class EstadoCertificado(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre_estado_cert",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre
    

class Derivador(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_derivador",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_derivador',
    )

    def __str__(self):
        return  self.nombre
    

class Conocer(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_conocer",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre


class PacienteRehabilitacion(models.Model):

    SI_NO_CHOICES = [
        (False, "NO"),
        (True, "SI"),
    ]
    
    id_paciente_area = models.ForeignKey(
        PacienteArea,
        on_delete=models.RESTRICT,
        related_name='id_paciente_area',
    )

    nombre_tutor = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default="NO",
        verbose_name="nombre_tutor",
    )

    celular_tutor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="celular_tutor",
    )

    hijos = models.IntegerField(
        null=False,
        blank=False,
        default=0,
    )

    id_estado_certificado = models.ForeignKey(
        EstadoCertificado,
        on_delete=models.RESTRICT,
        related_name='id_estado_certificado'
    )

    vencimiento_certificado = models.DateField(
        null=True,
        blank=True,
        verbose_name='vencimiento_certificado',
    )

    fecha_junta = models.DateField(
        null=True,
        blank=True,
        verbose_name='fecha_junta',
    )

    ven_presupuesto = models.BooleanField(
        choices=SI_NO_CHOICES,
        default=0,
        null=False,
        blank=False,
    )

    vencimiento_presupuesto = models.DateField(
        null=True,
        blank=True,
        verbose_name='vencimiento_presupuesto',
    )

    id_derivador = models.ForeignKey(
        Derivador,
        on_delete=models.RESTRICT,
        related_name="id_derivador"
    )

    id_obra_social = models.ForeignKey(
        ObraSocial,
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL,
        related_name='obra_social_paciente_rehabilitacion',
    )

    puerto_esperanza = models.BooleanField(
        choices=SI_NO_CHOICES,
        default=0,
        null=False,
        blank=False,
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_pac_rehabilitacion',
    )

    id_conocer = models.ForeignKey(
        Conocer,
        blank=True, 
        null=True,
        default=1,
        on_delete=models.SET_NULL,
        related_name='id_conocer_pac_rehab',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    diagnosticoCUD = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="diagnosticoCUD",
    )

    pre_ingreso = models.BooleanField(
        choices=SI_NO_CHOICES,
        default=0,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.id_paciente_area.id_area.nombre


class TipoDiscapacidad(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="nombre_tipo_discapacidad",
    )

    def __str__(self):
        return  self.nombre


class DiagnosticoEtiologico(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_diagnostico_etiologico",
    )

    id_tipo_discapacidad = models.ForeignKey(
        TipoDiscapacidad,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_tipo_discapacidad',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre
    

class DiagnosticoFuncional(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_diagnostico_funcional",
    )

    id_diagnostico_etiologico = models.ForeignKey(
        DiagnosticoEtiologico,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_diagnostico_etiologico_en_funcional',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre


class Alta(models.Model):

    fecha = models.DateField(
        null=True,
        blank=True,
        verbose_name='fecha_',
    )

    id_diagnostico_etiologico = models.ForeignKey(
        DiagnosticoEtiologico,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_diagnostico_etiologico_alta',
    )

    id_paciente_rehabilitacion = models.ForeignKey(
        PacienteRehabilitacion,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_paciente_rehabilitacion_alta',
    )

    fecha_alta = models.DateField(
        null=True,
        blank=True,
        verbose_name='fecha_alta',
    )

    dado_alta = models.BooleanField(
        default=0,
        null=False,
        blank=False,
    )


class AltaFuncional(models.Model):

    id_diagnostico_funcional = models.ForeignKey(
        DiagnosticoFuncional,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_diagnostico_funcional',
    )

    id_alta = models.ForeignKey(
        Alta,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_diagnostico_funcional',
    )

    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Obseraciones_alta_funcional",
        )
    
    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='usuario_alta_funcional',
    )

    def __str__(self):
        return  self.id_diagnostico_funcional.nombre
    

class AgendaRehab(models.Model):

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name='Fecha_rehab',
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha_fin_rehab',
    )

    hora_inicio = models.TimeField(
        null=False,
        blank=False,
        verbose_name="Hora de Inicio rehab",
    )

    hora_fin = models.TimeField(
        null=False,
        blank=False,
        verbose_name="Hora de Fin rehab",
    )

    id_dia = models.ForeignKey(
        Dia,
        on_delete=models.RESTRICT,
        related_name='dia_agenda_rehab'
    )

    id_tratamiento_rehab = models.ForeignKey(
        Tratamiento,
        on_delete=models.RESTRICT,
        related_name='tratamiento_agenda_rehab',
        null=False,
        blank=False,
    )

    id_paciente_area = models.ForeignKey(
        PacienteArea,
        on_delete=models.RESTRICT,
        related_name='id_paciente_area_agenda_rehab',
        null=False,
        blank=False,
    )

    id_profesional_area = models.ForeignKey(
        ProfesionalArea,
        on_delete=models.RESTRICT,
        related_name='id_profesional_area_agenda_rehab',
        null=False,
        blank=False,
    )

    tiempo = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=False,
        blank=False,
        verbose_name='tiempo_rehab'
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_agenda_rehab',
    )

    observaciones = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        verbose_name="Obseraciones_agenda_rehab",
        )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.id_paciente_area.id_paciente.nombre


class AsistenciaRehab(models.Model):

    fecha = models.DateField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Fecha Asistencia Rehab",
        )

    hora = models.TimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Hora Asistencia Rehab",
        )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Momento de carga",
        )

    id_agenda_rehab = models.ForeignKey(
        AgendaRehab,
        blank=True,
        null=True,
        default=None,
        on_delete=models.RESTRICT,
        related_name='agenda_rehab',
    )

    def __str__(self):
        return  self.id_agenda_rehab.id_paciente_area.id_paciente.nombre
    

class AsistenciaRehabTeorica(models.Model):

    id_agenda_rehab = models.ForeignKey(
        AgendaRehab,
        blank=True,
        null=True,
        default=None,
        on_delete=models.RESTRICT,
        related_name='agenda_rehab_teorica',
    )

    fecha = models.DateField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Fecha Asistencia Rehab",
        )
    
    def __str__(self):
        return  self.id_agenda_rehab.id_paciente_area.id_paciente.nombre
    

class TipoInforme(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_link",
    )

    def __str__(self):
        return self.nombre


class Informe(models.Model):

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name='Fecha_informe_rehab',
    )
    
    id_profesional = models.ForeignKey(
        Profesional,
        blank=False,
        null=False,
        on_delete=models.RESTRICT,
        related_name='profesional_informe',
    )

    id_profesional_tratamiento = models.ForeignKey(
        ProfesionalTratamiento,
        on_delete=models.RESTRICT,
        related_name='profesional_tratamiento_informe',
    )

    id_tipo_informe = models.ForeignKey(
        TipoInforme,
        blank=False,
        null=False,
        default=1,
        on_delete=models.RESTRICT,
        related_name='id_tipo_informe',
    )

    id_paciente = models.ForeignKey(
        Paciente,
        blank=False,
        null=False,
        on_delete=models.RESTRICT,
        related_name='paciente_informe',
    )

    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Obseraciones_alta_funcional",
    )

    activo = models.BooleanField(
        default=True,
        null=False,
        blank=False,
        verbose_name="Activo",
    )

    def __str__(self):
        return self.id_paciente.nombre


class Archivo(models.Model):

    archivo = models.FileField(
        upload_to='informes_rehab/',
    )
    
    id_informe = models.ForeignKey(
        Informe,
        blank=False,
        null=False,
        default=None,
        on_delete=models.RESTRICT,
        related_name='id_informe_archivo',
    )

    def delete(self, *args, **kwargs):
        if self.archivo and os.path.isfile(self.archivo.path):
            os.remove(self.archivo.path)

        super().delete(*args, **kwargs)

    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo.name)

    def __str__(self):
        return self.id_informe.id_paciente.nombre
    

class Link(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_link",
    )

    url = models.URLField(
        max_length=300,
        null=False,
        blank=False,
        verbose_name="url",
    )

    id_informe = models.ForeignKey(
        Informe,
        blank=False,
        null=False,
        default=None,
        on_delete=models.RESTRICT,
        related_name='id_informe_link',
    )

    def __str__(self):
        return self.id_informe.id_paciente.nombre + self.nombre
