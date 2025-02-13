from django import forms
from finanzas.models import Beneficiario, OrdenPago, DetalleOrden, Factura, Descuento, Concepto


class BeneficiarioUpdateForm(forms.ModelForm):
        
    class Meta:

        model = Beneficiario

        fields = [
            'nombre',
            'numero_cuit',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_cuit': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class OrdenPagoCreateForm(forms.ModelForm):
        
    class Meta:

        model = OrdenPago

        fields = [
            'fecha',
            'numero',
            'id_beneficiario',
            'total',
            'id_usuario',
        ]
        
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_beneficiario': forms.Select(attrs={'class': 'form-control custom-class'}),
            'total': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class DetalleOrdenPagoCreateForm(forms.ModelForm):

    def __init__(self, id_beneficiario = 0, *args, **kwargs):
        super(DetalleOrdenPagoCreateForm, self).__init__(*args, **kwargs)
        self.fields['id_factura'].queryset = Factura.objects.filter(id_beneficiario=id_beneficiario)
        
    id_factura = forms.ModelMultipleChoiceField(
        queryset=Factura.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
    
    class Meta:

        model = DetalleOrden

        fields = [
            'id_ordenpago',
            'id_factura',
            'importe',
        ]
        
        widgets = {
            'id_ordenpago': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_factura': forms.SelectMultiple(attrs={'class': 'form-control custom-class'}),
            'importe': forms.NumberInput(attrs={'class': 'form-control custom-class', 'step': '0.01'}),
        }


class DescuentoOrdenPagoCreateForm(forms.ModelForm):

    id_concepto = forms.ModelMultipleChoiceField(
        queryset=Concepto.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:

        model = Descuento

        fields = [
            'id_ordenpago',
            'id_concepto',
            'importe',
            'observaciones'
        ]

        widgets = {
            'id_ordenpago': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_concepto': forms.SelectMultiple(attrs={'class': 'form-control custom-class'}),
            'importe': forms.NumberInput(attrs={'class': 'form-control custom-class', 'step': '0.01'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class FacturaForm(forms.Form):

    def __init__(self, id_beneficiario=None, *args, **kwargs):
        super(FacturaForm, self).__init__(*args, **kwargs)
        self.fields['descuentos'].queryset = Concepto.objects.all()
        if id_beneficiario:
            self.fields['facturas'].queryset = Factura.objects.filter(id_beneficiario=id_beneficiario)
        

    id_ordenpago = forms.ModelMultipleChoiceField(
        queryset=OrdenPago.objects.none(),
        widget=forms.HiddenInput(),
    )

    facturas = forms.ModelMultipleChoiceField(
        queryset=Factura.objects.none(),
        widget=forms.Select(),
    )

    descuentos = forms.ModelMultipleChoiceField(
        queryset=Concepto.objects.none(),
        widget=forms.Select(),
    )


class DescuentoForm(forms.Form):

    def __init__(self, id_beneficiario=None, *args, **kwargs):
        super(DescuentoForm, self).__init__(*args, **kwargs)
        self.fields['descuentos'].queryset = Descuento.objects.all()