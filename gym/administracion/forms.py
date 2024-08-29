from django import forms
from .models import Paciente, PrestacionPaciente, ObraSocial, Prestacion


class PacienteCreateForm(forms.ModelForm):

    class Meta:

        model = Paciente

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'direccion',
            'telefono',
            'celular',
            'fecha_nacimiento',
            'id_obra_social',
            'id_estado_civil',
            'id_sexo',
            'id_localidad',
            'id_usuario',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'celular': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'fecha_nacimiento': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_estado_civil': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_sexo': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_localidad': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class PacienteUpdateForm(forms.ModelForm):

    class Meta:

        model = Paciente

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'direccion',
            'telefono',
            'celular',
            'fecha_nacimiento',
            'id_obra_social',
            'id_estado_civil',
            'id_sexo',
            'id_localidad',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'celular': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'fecha_nacimiento': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_estado_civil': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_sexo': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_localidad': forms.Select(attrs={'class': 'form-control custom-class'}),
        }


class PrestacionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PrestacionCreateForm, self).__init__(*args, **kwargs)
        self.fields['id_prestacion'].required = True
        self.fields['id_obra_social'].required = True

    class Meta:

        model = PrestacionPaciente

        fields = [
            'fecha_inicio',
            'fecha_fin',
            'id_prestacion',
            'id_paciente',
            'id_obra_social',
            ]
        
        widgets = {
            'fecha_inicio': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'fecha_fin': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_prestacion': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_paciente': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
        }


class ObraSocialForm(forms.ModelForm):

    class Meta:

        model = ObraSocial

        fields = [
            'nombre',
            'descripcion',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class PrestacionForm(forms.ModelForm):

    class Meta:

        model = Prestacion

        fields = [
            'nombre',
            'descripcion',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }