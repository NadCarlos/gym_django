from django import forms
from django.contrib.auth import (
    authenticate,
)
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Email Requerido')
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        empty_label="Selecciona un grupo"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'grupo']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email ya registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            grupo = self.cleaned_data.get('grupo')
            if grupo:
                user.groups.add(grupo)
        return user


class LoginForm(forms.Form):

    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Login: Usuario o contraseña incorrectos.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user