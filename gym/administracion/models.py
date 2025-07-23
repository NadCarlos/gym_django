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

    def __str__(self):
        return  self.apellido
    

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

    def __str__(self):
        return  self.id_tratamiento.nombre


class Dia(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    def __str__(self):
        return  self.nombre


class Agenda(models.Model):

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name='Fecha',
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha',
    )

    hora_inicio = models.TimeField(
        null=False,
        blank=False,
        verbose_name="Hora de Inicio",
    )

    hora_fin = models.TimeField(
        null=False,
        blank=False,
        verbose_name="Hora de Fin",
    )

    id_prestacion_paciente = models.ForeignKey(
        PrestacionPaciente,
        on_delete=models.RESTRICT,
        related_name='prestacion_paciente_agenda',
    )

    id_profesional_tratamiento = models.ForeignKey(
        ProfesionalTratamiento,
        on_delete=models.RESTRICT,
        related_name='profesional_tratamiento_agenda',
    )

    id_dia = models.ForeignKey(
        Dia,
        on_delete=models.RESTRICT,
        related_name='dia_agenda'
    )

    tiempo = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=False,
        blank=False,
        verbose_name='tiempo'
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_agenda',
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.id_profesional_tratamiento.id_profesional.apellido
    

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

    id_agenda = models.ForeignKey(
        Agenda,
        blank=True,
        null=True,
        default=None,
        on_delete=models.RESTRICT,
        related_name='agenda',
    )

    def __str__(self):
        return  self.id_prestacion_paciente.id_paciente.nombre
    

class TipoPago(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre


class Pago(models.Model):

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name='Fecha',
    )

    total = models.DecimalField(
        verbose_name='total',
        max_digits=10,
        decimal_places=2,
    )

    id_paciente = models.ForeignKey(
        Paciente,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='paciente_pago',
    )

    id_tipo_pago = models.ForeignKey(
        TipoPago,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='tipo_pago',
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_pago',
    )
    
    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )


class Plan(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    valor = models.DecimalField(
        verbose_name='valor_plan',
        max_digits=10,
        decimal_places=2,
    )

    descripcion = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_plan',
    )

    def __str__(self):
        return  self.nombre


class PacientePlan(models.Model):

    id_paciente = models.ForeignKey(
        Paciente,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='paciente_plan',
    )

    id_plan = models.ForeignKey(
        Plan,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='plan',
    )

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name='Fecha',
    )

    activo = models.BooleanField(
        default=1,
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
        related_name='usuario_paciente_plan',
    )


class Cuota(models.Model):

    imputado = models.DateField(
        null=False,
        blank=False,
        verbose_name='imputado',
    )

    id_paciente_plan = models.ForeignKey(
        PacientePlan,
        on_delete=models.RESTRICT,
        related_name='usuario_cuota',
    )

    valor = models.DecimalField(
        verbose_name='valor_cuota',
        max_digits=10,
        decimal_places=2,
    )

    anulado = models.BooleanField(
        default=0,
        null=False,
        blank=False,
    )


class DetallePago(models.Model):

    id_pago = models.ForeignKey(
        Pago,
        on_delete=models.RESTRICT,
        related_name='id_pago',
    )

    id_cuota = models.ForeignKey(
        Cuota,
        on_delete=models.RESTRICT,
        related_name='id_cuota',
    )

    importe = models.DecimalField(
        verbose_name='importe',
        max_digits=10,
        decimal_places=2,
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )


class Area(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Nombre",
    )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
    )

    def __str__(self):
        return  self.nombre
    

class PacienteArea(models.Model):
    
    id_area = models.ForeignKey(
        Area,
        on_delete=models.RESTRICT,
        related_name='id_area',
        default=1,
    )

    id_paciente = models.ForeignKey(
        Paciente,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='paciente_area',
    )

    momento_de_carga = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
    )

    id_usuario = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='usuario_pac_area',
    )

    def __str__(self):
        return  self.id_area.nombre