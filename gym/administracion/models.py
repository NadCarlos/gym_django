from django.db import models
from django.contrib.auth.models import User


class Pais(models.Model):

    nombre = models.CharField(max_length=50)

    def __str__(self):
        return  self.nombre


class Provincia(models.Model):

    nombre = models.CharField(max_length=50)

    pais = models.ForeignKey(
        Pais,
        on_delete=models.CASCADE,
        related_name='pais',
    )

    def __str__(self):
        return  self.nombre


class Localidad(models.Model):

    nombre = models.CharField(max_length=50)

    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name='localidad',
    )

    def __str__(self):
        return  self.nombre
    

class ObraSocial(models.Model):

    nombre = models.CharField(max_length=50)

    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return  self.nombre
    

class EstadoCivil(models.Model):

    nombre = models.CharField(max_length=50)

    def __str__(self):
        return  self.nombre
    

class Sexo(models.Model):

    nombre = models.CharField(max_length=50)

    def __str__(self):
        return  self.nombre
    

class Prestacion(models.Model):

    nombre = models.CharField(max_length=50)

    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return  self.nombre


class Paciente(models.Model):

    nombre = models.CharField(max_length=150)

    apellido = models.CharField(max_length=150)

    numero_dni = models.CharField(max_length=11)

    direccion = models.CharField(max_length=150)

    telefono = models.CharField(max_length=50, blank=True, null=True, editable=True)

    celular = models.CharField(max_length=50)

    fecha_nacimiento = models.DateField()

    momento_de_carga = models.DateTimeField(auto_now_add=True)

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usuario',
    )

    activo = models.BooleanField(default=1)

    id_obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.CASCADE,
        related_name='obra_social',
    )

    id_estado_civil = models.ForeignKey(
        EstadoCivil,
        on_delete=models.CASCADE,
        related_name='estado_civil_paciente',
    )

    id_sexo = models.ForeignKey(
        Sexo,
        on_delete=models.CASCADE,
        related_name='sexo',
    )

    id_localidad = models.ForeignKey(
        Localidad,
        on_delete=models.CASCADE,
        related_name='localidad',
    )

    def __str__(self):
        return  self.nombre


class PrestacionPaciente(models.Model):

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    activo = models.BooleanField(default=1)

    id_prestacion = models.ForeignKey(
        Prestacion,
        on_delete=models.CASCADE,
        related_name='prestacion',
    )

    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='paciente',
    )

    id_obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.CASCADE,
        related_name='obra_social_prestacion',
    )

    def __str__(self):
        return  self.id_paciente.nombre


class Asistencia(models.Model):

    fecha = models.DateField(auto_now_add=True)

    hora = models.TimeField(auto_now_add=True)

    momento_de_carga = models.DateTimeField(auto_now_add=True)

    id_prestacion_paciente = models.ForeignKey(
        PrestacionPaciente,
        on_delete=models.CASCADE,
        related_name='prestacion_paciente_asistencia',
    )

    def __str__(self):
        return  self.id_prestacion_paciente.id_paciente.nombre
