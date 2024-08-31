from typing import Any
from django.views import View
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.filters import AsistenciasFilter

from entrada.repositories.asistencia import AsistenciaRepository


asisteniaRepo = AsistenciaRepository()

@method_decorator(login_required(login_url='login'), name='dispatch')
class AsistenciasList(ListView):
    queryset = asisteniaRepo.get_all()
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = AsistenciasFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context#