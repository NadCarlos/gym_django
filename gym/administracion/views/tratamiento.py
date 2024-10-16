from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    TratamientoForm,
)

from administracion.repositories.tratamiento import TratamientoRepository


tratamientoRepo = TratamientoRepository()