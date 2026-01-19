from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from rehabilitacion.forms import(
    DiagnosticoEtiologicoCreateForm,
)

from rehabilitacion.repositories.diagnostico_etiologico import DiagnosticoEtiologicoRepository


diagnosticoEtiologicoRepo = DiagnosticoEtiologicoRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticosEtiologicosList(View):

    def get(self, request):
        diagnosticos_etiologicos = diagnosticoEtiologicoRepo.get_all()
        return render(
            request,
            'diagnosticos/etiologicos/list.html',
            dict(
                diagnosticos_etiologicos = diagnosticos_etiologicos,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoEtiologicoCreate(View):

    def get(self, request):
        form = DiagnosticoEtiologicoCreateForm()
        return render(
            request,
            'diagnosticos/etiologicos/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request):
        form = DiagnosticoEtiologicoCreateForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            nombre = nombre.upper()
            id_tipo_discapacidad = form.cleaned_data['id_tipo_discapacidad']
            diagnostico_etiologico_nuevo = diagnosticoEtiologicoRepo.create(
                nombre=nombre,
                id_tipo_discapacidad=id_tipo_discapacidad,
            )
            return redirect('diagnosticos_etiologicos_list')
        else:
            return redirect('error')