from django import forms
from administracion.models import Paciente, Asistencia


class AsistenciaCreateForm(forms.ModelForm):

    class Meta:

        model = Asistencia

        fields = [
            'id_prestacion_paciente',
            ]
        
        widgets = {
            'id_prestacion_paciente': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AsistenciaPublicCreateForm(forms.ModelForm):

    class Meta:

        model = Paciente
        fields = ['numero_dni',]
        widgets = {
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
        }