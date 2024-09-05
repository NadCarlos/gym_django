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
class AsistenciasList(View):
    queryset = asisteniaRepo.get_all()
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get(self, request):
        asistencias = self.queryset
        return render (
            request,
            self.template_name,
            dict(
                asistencias=asistencias,
            )
        )

class AsistenciasList(View):
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get(self, request):
        # Instanciar el filtro con los datos enviados por el formulario
        filterset = AsistenciasFilter(request.GET, queryset=asisteniaRepo.get_all())

        # Obtener el queryset filtrado
        asistencias=filterset.qs
        return render(
            request,
            self.template_name,
            {
                'asistencias': asistencias,  # Pasamos las asistencias filtradas
                'form': filterset.form,  # Pasamos el formulario del filtro al template
            }
        )
    


"""    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context"""
    
"""
def post(self, request, *args, **kwargs):
    armo 1 form que:
    recibir las 2 fechas
    retornar:
    qs.filter(fecha__range(finicio, ffin))
    qs.filter(fecha__gte=finicio, fecha__lt)

"""