from django import forms
from finanzas.models import Beneficiario


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