from django.db import models
from django.contrib.auth.models import User

from administracion.models import (
    PacienteArea,
    ObraSocial,
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
        null=False,
        blank=False,
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

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.id_paciente_area.id_area.nombre


class Familia(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_familia",
    )

    def __str__(self):
        return  self.nombre


class Diagnostico(models.Model):

    nombre = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Nombre_diagnostico",
    )

    id_familia = models.ForeignKey(
        Familia,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_familia',
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

    id_diagnostico = models.ForeignKey(
        Diagnostico,
        blank=False, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='id_diagnostico_alta',
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