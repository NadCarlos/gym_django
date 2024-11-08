from django import forms
from .models import Paciente, PrestacionPaciente, ObraSocial, Prestacion, Profesional, Tratamiento, ProfesionalTratamiento, Agenda


class PacienteCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PacienteCreateForm, self).__init__(*args, **kwargs)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)
        
    class Meta:

        model = Paciente

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'direccion',
            'telefono',
            'celular',
            'observaciones',
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
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_estado_civil': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_sexo': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_localidad': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class PacienteUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PacienteUpdateForm, self).__init__(*args, **kwargs)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)

    class Meta:

        model = Paciente

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'direccion',
            'telefono',
            'celular',
            'observaciones',
            'fecha_nacimiento',
            'id_obra_social',
            'id_estado_civil',
            'id_sexo',
            'id_localidad',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class','maxlength': '8'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'celular': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
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
        self.fields['id_prestacion'].queryset = Prestacion.objects.filter(activo=True)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)

    class Meta:

        model = PrestacionPaciente

        fields = [
            'fecha_inicio',
            'id_prestacion',
            'id_paciente',
            'id_obra_social',
            ]
        
        widgets = {
            'fecha_inicio': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_prestacion': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_paciente': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_obra_social': forms.Select(attrs={'class': 'form-control custom-class'}),
        }


class PrestacionUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PrestacionUpdateForm, self).__init__(*args, **kwargs)
        self.fields['id_prestacion'].required = True
        self.fields['id_obra_social'].required = True
        self.fields['id_prestacion'].queryset = Prestacion.objects.filter(activo=True)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)

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


class ProfesionalCreateForm(forms.ModelForm):
    class Meta:

        model = Profesional

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'matricula',
            'direccion',
            'celular',
            'fecha_nacimiento',
            'id_sexo',
            'id_localidad',
            'id_usuario',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'matricula': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'celular': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_sexo': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_localidad': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class ProfesionalUpdateForm(forms.ModelForm):
    class Meta:

        model = Profesional

        fields = [
            'nombre',
            'apellido',
            'numero_dni',
            'matricula',
            'direccion',
            'celular',
            'fecha_nacimiento',
            'id_sexo',
            'id_localidad',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'matricula': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'celular': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_sexo': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_localidad': forms.Select(attrs={'class': 'form-control custom-class'}),
        }


class TratamientoForm(forms.ModelForm):

    class Meta:

        model = Tratamiento

        fields = [
            'nombre',
            'descripcion',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class TratamientoProfesionalCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TratamientoProfesionalCreateForm, self).__init__(*args, **kwargs)
        self.fields['id_tratamiento'].required = True
        self.fields['id_tratamiento'].queryset = Tratamiento.objects.filter(activo=True)

    class Meta:

        model = ProfesionalTratamiento

        fields = [
            'fecha_inicio',
            'id_tratamiento',
            'id_profesional',
            ]
        
        widgets = {
            'fecha_inicio': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_tratamiento': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_profesional': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AgendaCreateForm(forms.ModelForm):

    class Meta:

        model = Agenda

        fields = [
            'fecha',
            'hora_inicio',
            'hora_fin',
            'id_dia',
            'id_profesional_tratamiento',
            'id_usuario',
            ]
        
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'id_dia': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_profesional_tratamiento': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }