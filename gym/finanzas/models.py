from django.db import models


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
    
    serie = models.CharField(
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

    importe = models.FloatField(
        null=False,
        blank=False,
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
