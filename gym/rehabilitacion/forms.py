from django import forms
from django.db.models import Min, Case, When, IntegerField
from rehabilitacion.models import (
    AgendaRehab,
    Alta,
    AltaEtiologico,
    AltaFuncional,
    AltaTipoDiscapacidad,
    Archivo,
    Conocer,
    DiagnosticoEtiologico,
    DiagnosticoFuncional,
    Informe,
    Link,
    ObraSocial,
    PacienteRehabilitacion,
    TipoDiscapacidad,
    TipoInforme,
    Turno,
)
from administracion.models import Paciente, PacienteArea, Profesional, ProfesionalTratamiento, Tratamiento
from administracion.repositories.profesional import ProfesionalRepository


profesionalRepo = ProfesionalRepository()


class PacienteRehabilitacionCreateForm(forms.ModelForm):

    SI_NO_CHOICES = [
        (0, "NO"),
        (1, "SI"),
    ]

    puerto_esperanza = forms.ChoiceField(
        choices=SI_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control custom-class'})
    )

    pre_ingreso = forms.ChoiceField(
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
        self.fields['id_conocer'].queryset = Conocer.objects.filter(activo=True)
        self.fields['id_derivador'].initial = None
        self.fields['id_derivador'].empty_label = "Seleccione una opcion"
        self.fields['id_conocer'].initial = None
        self.fields['id_conocer'].empty_label = "Seleccione una opcion"

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
            'numero_afiliado',
            'id_conocer',
            'id_usuario',
            'diagnosticoCUD',
            'pre_ingreso',
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
            'numero_afiliado': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_conocer': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'diagnosticoCUD': forms.TextInput(attrs={'class': 'form-control custom-class','id':'diagnosticoCUD'}),
        }


class PacienteRehabilitacionUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PacienteRehabilitacionUpdateForm, self).__init__(*args, **kwargs)
        self.fields['id_obra_social'].queryset = ObraSocial.objects.filter(activo=True)
        self.fields['id_conocer'].queryset = Conocer.objects.filter(activo=True)

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
            'numero_afiliado',
            'id_conocer',
            'diagnosticoCUD',
            'pre_ingreso',
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
            'numero_afiliado': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_conocer': forms.Select(attrs={'class': 'form-control custom-class'}),
            'puerto_esperanza': forms.Select(attrs={'class': 'form-control custom-class'}),
            'diagnosticoCUD': forms.TextInput(attrs={'class': 'form-control custom-class','id':'diagnosticoCUD'}),
            'pre_ingreso': forms.Select(attrs={'class': 'form-control custom-class'}),

        }


class AltaCreateForm(forms.ModelForm):

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    tipos_discapacidad = forms.ModelMultipleChoiceField(
        queryset=TipoDiscapacidad.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 8}),
        required=True,
    )

    diagnosticos_etiologicos = forms.ModelMultipleChoiceField(
        queryset=DiagnosticoEtiologico.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 8}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipos_discapacidad'].queryset = TipoDiscapacidad.objects.all().order_by('nombre')
        self.fields['diagnosticos_etiologicos'].queryset = DiagnosticoEtiologico.objects.all().order_by('nombre')

    class Meta:
        model = Alta
        fields = ['fecha', 'id_paciente_rehabilitacion']

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_diagnostico_funcional'].queryset = DiagnosticoFuncional.objects.all().order_by('nombre')
        self.fields['id_diagnostico_funcional'].empty_label = "Seleccione una opcion"

    class Meta:
        model = AltaFuncional

        fields = [
            'id_alta',
            'id_diagnostico_funcional',
            'observaciones',
            'id_usuario',
            ]
        
        widgets = {
            'id_alta': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_diagnostico_funcional': forms.Select(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AltaTipoDiscapacidadCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_tipo_discapacidad'].queryset = TipoDiscapacidad.objects.all().order_by('nombre')
        self.fields['id_tipo_discapacidad'].empty_label = "Seleccione una opcion"

    class Meta:
        model = AltaTipoDiscapacidad

        fields = [
            'id_alta',
            'id_tipo_discapacidad',
            'observaciones',
            'id_usuario',
        ]

        widgets = {
            'id_alta': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_tipo_discapacidad': forms.Select(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'id_usuario': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class AltaEtiologicoCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_diagnostico_etiologico'].queryset = DiagnosticoEtiologico.objects.all().order_by('nombre')
        self.fields['id_diagnostico_etiologico'].empty_label = "Seleccione una opcion"

    class Meta:
        model = AltaEtiologico

        fields = [
            'id_alta',
            'id_diagnostico_etiologico',
            'observaciones',
            'id_usuario',
        ]

        widgets = {
            'id_alta': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'id_diagnostico_etiologico': forms.Select(attrs={'class': 'form-control custom-class'}),
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
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class DiagnosticoFuncionalCreateForm(forms.ModelForm):

    class Meta:
        model = DiagnosticoFuncional
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


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


class TurnoCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ids_pacientes = (
            PacienteArea.objects
            .annotate(
                prioridad=Case(
                    When(id_area=2, then=1),
                    When(id_area=3, then=2),
                    When(id_area=1, then=3),
                    default=99,
                    output_field=IntegerField(),
                )
            )
            .values('id_paciente')
            .annotate(min_prioridad=Min('prioridad'))
            .values_list('id_paciente', flat=True)
        )

        self.fields['paciente_id'].queryset = (
            Paciente.objects
            .filter(id__in=ids_pacientes, activo=True)
            .order_by('apellido', 'nombre')
        )
        self.fields['paciente_id'].empty_label = "Seleccione un paciente"
        self.fields['paciente_id'].label_from_instance = (lambda paciente: f"{paciente.apellido}, {paciente.nombre} - DNI {paciente.numero_dni}")

        self.fields['profesional_id'].queryset = Profesional.objects.filter(
            activo=True,
            profesional_area__id_area=2,
        ).distinct().order_by('apellido', 'nombre')
        self.fields['profesional_id'].empty_label = "Seleccione un profesional"
        self.fields['profesional_id'].label_from_instance = (
            lambda profesional: f"{profesional.apellido}, {profesional.nombre}"
        )

        self.fields['tratamiento_id'].queryset = Tratamiento.objects.none()
        self.fields['tratamiento_id'].empty_label = "Seleccione un tratamiento"
        self.fields['tratamiento_id'].widget.attrs['disabled'] = 'disabled'

        profesional_id = None
        if self.is_bound:
            profesional_id = self.data.get('profesional_id')

        if profesional_id:
            tratamientos_ids = ProfesionalTratamiento.objects.filter(
                id_profesional_id=profesional_id,
                activo=True,
            ).values_list('id_tratamiento_id', flat=True)
            self.fields['tratamiento_id'].queryset = Tratamiento.objects.filter(
                id__in=tratamientos_ids,
                activo=True,
            ).order_by('nombre')
            self.fields['tratamiento_id'].widget.attrs.pop('disabled', None)

    def clean(self):
        cleaned_data = super().clean()
        profesional = cleaned_data.get('profesional_id')
        tratamiento = cleaned_data.get('tratamiento_id')

        if profesional and tratamiento:
            tratamiento_valido = ProfesionalTratamiento.objects.filter(
                id_profesional=profesional,
                id_tratamiento=tratamiento,
                activo=True,
            ).exists()
            if not tratamiento_valido:
                self.add_error(
                    'tratamiento_id',
                    'El tratamiento seleccionado no pertenece al profesional elegido.',
                )

        return cleaned_data

    class Meta:
        model = Turno
        fields = [
            'paciente_id',
            'profesional_id',
            'tratamiento_id',
            'fecha',
            'hora',
            'motivo',
        ]

        widgets = {
            'paciente_id': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'select-paciente'}),
            'profesional_id': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'select-profesional'}),
            'tratamiento_id': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'select-tratamiento'}),
            'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control custom-class', 'id': 'motivoInput'}),
        }


class TurnoUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['profesional_id'].queryset = Profesional.objects.filter(
            activo=True,
            profesional_area__id_area=2,
        ).distinct().order_by('apellido', 'nombre')
        self.fields['profesional_id'].empty_label = "Seleccione un profesional"
        self.fields['profesional_id'].label_from_instance = (
            lambda profesional: f"{profesional.apellido}, {profesional.nombre}"
        )

        self.fields['tratamiento_id'].queryset = Tratamiento.objects.none()
        self.fields['tratamiento_id'].empty_label = "Seleccione un tratamiento"
        self.fields['tratamiento_id'].widget.attrs['disabled'] = 'disabled'

        profesional_id = None

        if self.is_bound:
            profesional_id = self.data.get('profesional_id')

        elif self.instance and self.instance.pk:
            profesional_id = self.instance.profesional_id_id

        if profesional_id:
            tratamientos_ids = ProfesionalTratamiento.objects.filter(
                id_profesional_id=profesional_id,
                activo=True,
            ).values_list('id_tratamiento_id', flat=True)
            self.fields['tratamiento_id'].queryset = Tratamiento.objects.filter(
                id__in=tratamientos_ids,
                activo=True,
            ).order_by('nombre')
            self.fields['tratamiento_id'].widget.attrs.pop('disabled', None)

    def clean(self):
        cleaned_data = super().clean()
        profesional = cleaned_data.get('profesional_id')
        tratamiento = cleaned_data.get('tratamiento_id')

        if profesional and tratamiento:
            tratamiento_valido = ProfesionalTratamiento.objects.filter(
                id_profesional=profesional,
                id_tratamiento=tratamiento,
                activo=True,
            ).exists()
            if not tratamiento_valido:
                self.add_error(
                    'tratamiento_id',
                    'El tratamiento seleccionado no pertenece al profesional elegido.',
                )

        return cleaned_data

    class Meta:
        model = Turno
        fields = [
            'profesional_id',
            'tratamiento_id',
            'fecha',
            'hora',
        ]

        widgets = {
            'profesional_id': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'select-profesional'}),
            'tratamiento_id': forms.Select(attrs={'class': 'form-control custom-class', 'id': 'select-tratamiento'}),
            'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'time'}),
        }


class AsistenciaRehabPublicCreateForm(forms.ModelForm):

    class Meta:

        model = Paciente
        fields = ['numero_dni',]
        widgets = {
            'numero_dni': forms.NumberInput(attrs={'class': 'form-control custom-class'}),
        }


class InformeCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_profesional'].queryset = profesionalRepo.filter_profesional_area(id_area=2)
        self.fields['id_tipo_informe'].queryset = TipoInforme.objects.all().order_by('nombre')

        # Por defecto no se muestran prestaciones hasta elegir profesional.
        self.fields['id_profesional_tratamiento'].queryset = ProfesionalTratamiento.objects.none()
        self.fields['id_profesional_tratamiento'].widget.attrs['disabled'] = 'disabled'

        profesional_id = None
        if self.is_bound:
            profesional_id = self.data.get('id_profesional')
        elif self.instance and self.instance.pk:
            profesional_id = self.instance.id_profesional_id

        if profesional_id:
            queryset = ProfesionalTratamiento.objects.filter(
                id_profesional_id=profesional_id,
                activo=True,
            )
            self.fields['id_profesional_tratamiento'].queryset = queryset
            self.fields['id_profesional_tratamiento'].widget.attrs.pop('disabled', None)

    def clean(self):
        cleaned_data = super().clean()
        profesional = cleaned_data.get('id_profesional')
        profesional_tratamiento = cleaned_data.get('id_profesional_tratamiento')

        if profesional and profesional_tratamiento:
            if (
                profesional_tratamiento.id_profesional_id != profesional.id
                or not profesional_tratamiento.activo
            ):
                self.add_error(
                    'id_profesional_tratamiento',
                    'La prestación seleccionada no corresponde al profesional o no está activa.',
                )
        return cleaned_data

    class Meta:

        model = Informe

        fields = [
            'fecha',
            'id_tipo_informe',
            'id_profesional',
            'id_profesional_tratamiento',
            'id_paciente',
            'observaciones',
            ]
        
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'),attrs={'class': 'form-control', 'placeholder': 'Select a date','type': 'date'}),
            'id_tipo_informe': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_profesional': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_profesional_tratamiento': forms.Select(attrs={'class': 'form-control custom-class'}),
            'id_paciente': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control custom-class'}),
        }


class ArchivoCreateForm(forms.ModelForm):

    class Meta:

        model = Archivo

        fields = [
            'archivo',
            'id_informe',
            ]
        
        widgets = {
            'id_informe': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }


class LinkCreateForm(forms.ModelForm):

    class Meta:

        model = Link

        fields = [
            'nombre',
            'url',
            'id_informe',
            ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control custom-class'}),
            'url': forms.URLInput(attrs={'class': 'form-control custom-class'}),
            'id_informe': forms.HiddenInput(attrs={'class': 'form-control custom-class'}),
        }
