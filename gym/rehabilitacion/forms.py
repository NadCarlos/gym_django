from django import forms
from rehabilitacion.models import PacienteRehabilitacion, ObraSocial, Alta, Diagnostico, Familia


class PacienteRehabilitacionCreateForm(forms.ModelForm):

    SI_NO_CHOICES = [
        (0, "NO"),
        (1, "SI"),
    ]

    puerto_esperanza = forms.ChoiceField(
        choices=SI_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control custom-class'})
    )

    ven_presupuesto = forms.ChoiceField(
        choices=SI_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control custom-class','id':'ven_presupuesto'})
    )

    def __init__(self, *args, **kwargs):
        super(PacienteRehabilitacionCreateForm, self).__init__(*args, **kwargs)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)

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
            'id_obra_social',
            'id_usuario',
            ]
        
        widgets = {
            'id_paciente_area': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'nombre_tutor': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'celular_tutor': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'hijos': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'id_estado_certificado': forms.Select(attrs={'class': 'form-control custom-class', 'id':'id_id_estado_certificado'}),
            'vencimiento_certificado': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date', 'id':'id_vencimiento_certificado'}),
            'fecha_junta': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date', 'id':'id_fecha_junta'}),
            #'ven_presupuesto': forms.Select(attrs={'class': 'form-control custom-class'}),
            'vencimiento_presupuesto': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date','id':'vencimiento_presupuesto'}),
            'id_derivador': forms.Select(attrs={'class': 'form-control custom-class'}),
            #'puerto_esperanza': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AltaCreateForm(forms.ModelForm):

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    id_diagnostico = forms.ModelChoiceField(
        queryset=Diagnostico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Alta
        fields = ['fecha', 'id_diagnostico', 'id_paciente_rehabilitacion']

        widgets = {
            'id_paciente_rehabilitacion': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }