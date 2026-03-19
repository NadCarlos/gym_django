from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
            diagnosticoEtiologicoRepo.create(
                nombre=nombre,
            )
            return redirect('diagnosticos_etiologicos_list')
        else:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoEtiologicoUpdate(View):

    def get(self, request, id):
        diagnostico_etiologico = diagnosticoEtiologicoRepo.filter_by_id(id=id).first()
        if diagnostico_etiologico is None:
            messages.error(request, 'No se encontró el diagnóstico etiológico.')
            return redirect('diagnosticos_etiologicos_list')
        form = DiagnosticoEtiologicoCreateForm(instance=diagnostico_etiologico)
        return render(
            request,
            'diagnosticos/etiologicos/update.html',
            dict(
                form=form,
                diagnostico=diagnostico_etiologico,
            )
        )

    def post(self, request, id):
        diagnostico_etiologico = diagnosticoEtiologicoRepo.filter_by_id(id=id).first()
        if diagnostico_etiologico is None:
            messages.error(request, 'No se encontró el diagnóstico etiológico.')
            return redirect('diagnosticos_etiologicos_list')
        form = DiagnosticoEtiologicoCreateForm(request.POST, instance=diagnostico_etiologico)
        if form.is_valid():
            diagnosticoEtiologicoRepo.update(
                diagnostico_etiologico=diagnostico_etiologico,
                nombre=form.cleaned_data['nombre'].upper(),
            )
            messages.success(request, 'Diagnóstico etiológico actualizado correctamente.')
            return redirect('diagnosticos_etiologicos_list')
        return render(
            request,
            'diagnosticos/etiologicos/update.html',
            dict(
                form=form,
                diagnostico=diagnostico_etiologico,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoEtiologicoDelete(View):

    def get(self, request, id):
        diagnostico_etiologico = diagnosticoEtiologicoRepo.filter_by_id(id=id).first()
        if diagnostico_etiologico is None:
            messages.error(request, 'No se encontró el diagnóstico etiológico.')
            return redirect('diagnosticos_etiologicos_list')

        if diagnosticoEtiologicoRepo.has_alta_relation(diagnostico_etiologico):
            messages.error(
                request,
                'No se puede eliminar porque está relacionado a un alta activa. '
                'Primero debe quitar esa relación.'
            )
            return redirect('diagnosticos_etiologicos_list')

        diagnosticoEtiologicoRepo.delete(diagnostico_etiologico=diagnostico_etiologico)
        messages.success(request, 'Diagnóstico etiológico eliminado correctamente.')
        return redirect('diagnosticos_etiologicos_list')
