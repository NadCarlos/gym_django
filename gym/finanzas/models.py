from django.db import models
from django.contrib.auth.models import User


class Beneficiario(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="nombre"
        )
    
    numero_cuit = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        editable=True,
        verbose_name="Numero cuit"
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
    
    def __str__(self):
        return  self.nombre
    

class Factura(models.Model):

    tipo = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="tipo"
        )
    
    pto_vta = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="nombre"
        )
    
    numero = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="nombre"
        )
    
    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name="fecha"
    )

    importe = models.DecimalField(
        null=False,
        blank=False,
        max_digits=20,
        decimal_places=2,
        verbose_name="importe"
    )

    id_beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        related_name='id_beneficiario',
    )

    def __str__(self):
        return  self.numero   


class OrdenPago(models.Model):

    fecha = models.DateField(
        null=False,
        blank=False,
        verbose_name="fecha"
    )

    numero = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="numero"
        )

    id_beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        related_name='id_beneficiario_ordenpago',
    )

    total = models.DecimalField(
        verbose_name='total',
        max_digits=10,
        decimal_places=2,
    )

    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Obseraciones",
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
        related_name='usuario_ordenpago',
    )

    def __str__(self):
        return  self.id_beneficiario.nombre


class Concepto(models.Model):

    nombre = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="nombre"
        )

    activo = models.BooleanField(
        default=1,
        null=False,
        blank=False,
        )
    
    def __str__(self):
        return  self.nombre


class Descuento(models.Model):

    id_concepto = models.ForeignKey(
        Concepto,
        on_delete=models.RESTRICT,
        related_name='id_concepto_dto',
    )

    id_ordenpago = models.ForeignKey(
        OrdenPago,
        on_delete=models.RESTRICT,
        related_name='id_ordenpago_dto',
    )

    importe = models.DecimalField(
        verbose_name='importe',
        max_digits=10,
        decimal_places=2,
    )

    observaciones = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Obseraciones",
        )
    

class DetalleOrden(models.Model):

    id_ordenpago = models.ForeignKey(
        OrdenPago,
        on_delete=models.RESTRICT,
        related_name='id_ordenpago_detalleorden',
    )

    id_factura = models.ForeignKey(
        Factura,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        related_name='id_factura_detalleorden',
    )

    importe = models.DecimalField(
        verbose_name='importe',
        max_digits=10,
        decimal_places=2,
    )