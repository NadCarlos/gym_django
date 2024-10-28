from django.db import models
from django.contrib.auth.models import User


class Pais(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Pais"
        )

    def __str__(self):
        return  self.nombre


class Provincia(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Provincia"
        )

    pais = models.ForeignKey(
        Pais,
        on_delete=models.RESTRICT,
        related_name='pais',
    )

    def __str__(self):
        return  self.nombre


class Localidad(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Localidad"
        )

    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.RESTRICT,
        related_name='localidad',
    )

    def __str__(self):
        return  self.nombre
    

class ObraSocial(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        )
    
    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
        )

    def __str__(self):
        return  self.nombre
    

class EstadoCivil(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        )

    def __str__(self):
        return  self.nombre
    

class Sexo(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        )

    def __str__(self):
        return  self.nombre
    

class Prestacion(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        )
    
    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
        )

    def __str__(self):
        return  self.nombre


class Paciente(models.Model):

    nombre = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Nombre",
        )

    apellido = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Apellido"
        )

    numero_dni = models.CharField(
        max_length=8,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Numero DNI"
        )

    direccion = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Direccion",
        )

    telefono = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        editable=True,
        verbose_name="Telefono Fijo",
        )

    celular = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numero Celular",
        )

    fecha_nacimiento = models.DateField(
        null=False,
        blank=False,
        verbose_name="Fecha de nacimiento",
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        )
    
    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Obseraciones",
        )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
        )

    id_obra_social = models.ForeignKey(
        ObraSocial,
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL,
        related_name='obra_social',
    )

    id_estado_civil = models.ForeignKey(
        EstadoCivil,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='estado_civil_paciente',
    )

    id_sexo = models.ForeignKey(
        Sexo,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sexo',
    )

    id_localidad = models.ForeignKey(
        Localidad,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='localidad',
    )

    def __str__(self):
        return  self.nombre


class PrestacionPaciente(models.Model):

    fecha_inicio = models.DateField(
        null=False,
        blank=False,
        verbose_name='Inicio de la prestacion'
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fin de la prestacion'
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
        )

    id_prestacion = models.ForeignKey(
        Prestacion,
        blank=True,
        null=False,
        default="",
        on_delete=models.SET_DEFAULT,
        related_name='prestacion',
    )

    id_paciente = models.ForeignKey(
        Paciente,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='paciente',
    )

    id_obra_social = models.ForeignKey(
        ObraSocial,
        blank=True,
        null=False,
        default="",
        on_delete=models.SET_DEFAULT,
        related_name='obra_social_prestacion',
    )

    def __str__(self):
        return  self.id_paciente.nombre


class Asistencia(models.Model):

    fecha = models.DateField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Fecha Asistencia",
        )

    hora = models.TimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Hora Asistencia",
        )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Momento de carga",
        )

    id_prestacion_paciente = models.ForeignKey(
        PrestacionPaciente,
        on_delete=models.RESTRICT,
        related_name='prestacion_paciente_asistencia',
    )

    def __str__(self):
        return  self.id_prestacion_paciente.id_paciente.nombre


class Profesional(models.Model):

    nombre = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    apellido = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Apellido"
    )
    
    numero_dni = models.CharField(
        max_length=8,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Numero DNI"
    )
    
    matricula = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name="Matricula",
    )

    direccion = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Direccion",
    )

    celular = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numero Celular",
    )
    
    fecha_nacimiento = models.DateField(
        null=False,
        blank=False,
        verbose_name="Fecha de nacimiento",
    )

    id_localidad = models.ForeignKey(
        Localidad,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='localidad_prof',
    )

    id_sexo = models.ForeignKey(
        Sexo,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sexo_prof',
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_prof',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )
    

class Tratamiento(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre


class ProfesionalTratamiento(models.Model):

    id_profesional = models.ForeignKey(
        Profesional,
        on_delete=models.RESTRICT,
        related_name='profesional',
    )

    id_tratamiento = models.ForeignKey(
        Tratamiento,
        on_delete=models.RESTRICT,
        related_name='tratamiento',
    )

    fecha_inicio = models.DateField(
        null=False,
        blank=False,
        verbose_name='Inicio del Tratamiento'
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )