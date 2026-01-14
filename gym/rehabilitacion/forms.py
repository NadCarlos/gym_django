from django import forms
from rehabilitacion.models import PacienteRehabilitacion, ObraSocial, Alta, DiagnosticoEtiologico, TipoDiscapacidad, AltaFuncional, DiagnosticoFuncional, AgendaRehab


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
            'diagnosticoCUD',
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
            'diagnosticoCUD': forms.TextInput(attrs={'class': 'form-control custom-class','id':'diagnosticoCUD'}),
        }


class PacienteRehabilitacionUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PacienteRehabilitacionUpdateForm, self).__init__(*args, **kwargs)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)

    class Meta:
        model = PacienteRehabilitacion
        fields = [
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
            'diagnosticoCUD',
        ]
        widgets = {
            'nombre_tutor': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'celular_tutor': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'hijos': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'id_estado_certificado': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'id_id_estado_certificado'}),
            'vencimiento_certificado': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'id': 'id_vencimiento_certificado'}),
            'fecha_junta': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'id': 'id_fecha_junta'}),
            'ven_presupuesto': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'ven_presupuesto'}),
            'vencimiento_presupuesto': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'id': 'vencimiento_presupuesto'}),
            'id_derivador': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
            'puerto_esperanza': forms.Select(attrs={'class': 'form-control custom-class'}),
            'diagnosticoCUD': forms.TextInput(attrs={'class': 'form-control custom-class','id':'diagnosticoCUD'}),
        }



class AltaCreateForm(forms.ModelForm):

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    tipo_discapacidad = forms.ModelChoiceField(
        queryset=TipoDiscapacidad.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control','id':'id_tipo_discapacidad'})
    )

    id_diagnostico_etiologico = forms.ModelChoiceField(
        queryset=DiagnosticoEtiologico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control','id':'id_diagnostico_etiologico'})
    )

    class Meta:
        model = Alta
        fields = ['fecha', 'id_diagnostico_etiologico', 'tipo_discapacidad', 'id_paciente_rehabilitacion']

        widgets = {
            'id_paciente_rehabilitacion': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AltaTerminateForm(forms.ModelForm):

    class Meta:
        model = Alta
        fields = ['fecha_alta', 'dado_alta']

        widgets = {
            'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'id': 'fecha_alta'}),
            'dado_alta': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AltaFuncionalCreateForm(forms.ModelForm):

    class Meta:
        model = AltaFuncional

        fields = [
            'id_alta',
            'observaciones',
            'id_usuario',
            ]
        
        widgets = {
            'id_alta': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class TipoDiscapacidadCreateForm(forms.ModelForm):

    class Meta:
        model = TipoDiscapacidad

        fields = [
            'nombre',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class DiagnosticoEtiologicoCreateForm(forms.ModelForm):

    class Meta:
        model = DiagnosticoEtiologico

        fields = [
            'nombre',
            'id_tipo_discapacidad',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_tipo_discapacidad': forms.Select(attrs={'class': 'form-control custom-class'}),
        }


class DiagnosticoFuncionalCreateForm(forms.ModelForm):

    id_diagnostico_etiologico = forms.ModelChoiceField(
        queryset=DiagnosticoEtiologico.objects.select_related("id_tipo_discapacidad").all(),
        widget=forms.Select(attrs={'class': 'form-control custom-class'})
    )

    class Meta:
        model = DiagnosticoFuncional
        fields = ['nombre', 'id_diagnostico_etiologico']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cambiar el texto que se muestra en el select
        self.fields['id_diagnostico_etiologico'].label_from_instance = (
            lambda obj: f"{obj.nombre} — {obj.id_tipo_discapacidad.nombre}"
        )


class AgendaRehabCreateForm(forms.ModelForm):

    class Meta:

        model = AgendaRehab

        fields = [
            'fecha',
            'hora_inicio',
            'hora_fin',
            'id_dia',
            'id_usuario',
            'observaciones',
            ]
        
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'),attrs={'readonly':'readonly', 'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'id_dia': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class AgendaRehabUpdateForm(forms.ModelForm):

    class Meta:

        model = AgendaRehab

        fields = [
            'hora_inicio',
            'hora_fin',
            'id_dia',
            'observaciones',
            ]
        
        widgets = {
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'id_dia': forms.Select(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }