from django import forms
from rehabilitacion.models import PacienteRehabilitacion, EstadoCertificado, Derivador


class PacienteRehabilitacionCreateForm(forms.ModelForm):
        
    class Meta:

        model = PacienteRehabilitacion

        fields = [
            'id_paciente_area',
            'nombre_tutor',
            'celular_tutor',
            'hijos',
            'id_estado_certificado',
            'vencimiento_certificado',
            'fecha_junta',
            'ven_presupuesto',
            'vencimiento_presupuesto',
            'id_derivador',
            'puerto_esperanza',
            'id_usuario',
            ]
        
        widgets = {
            'id_paciente_area': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'nombre_tutor': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'celular_tutor': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'hijos': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'id_estado_certificado': forms.Select(attrs={'class': 'form-control custom-class'}),
            'vencimiento_certificado': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'fecha_junta': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'ven_presupuesto': forms.Select(attrs={'class': 'form-control custom-class'}),
            'vencimiento_presupuesto': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_derivador': forms.Select(attrs={'class': 'form-control custom-class'}),
            'puerto_esperanza': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }