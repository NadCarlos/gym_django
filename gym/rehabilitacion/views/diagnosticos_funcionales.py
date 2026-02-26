from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from rehabilitacion.forms import(
    DiagnosticoFuncionalCreateForm,
)


from rehabilitacion.repositories.diagnostico_funcional import DiagnosticoFuncionalRepository


diagnosticoFuncionalRepo = DiagnosticoFuncionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoFuncionalList(View):

    def get(self, request):
        diagnosticos_funcionales = diagnosticoFuncionalRepo.get_all()
        return render(
            request,
            'diagnosticos/funcionales/list.html',
            dict(
                diagnosticos_funcionales = diagnosticos_funcionales,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoFuncionalCreate(View):

    def get(self, request):
        form = DiagnosticoFuncionalCreateForm()
        return render(
            request,
            'diagnosticos/funcionales/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request):
        form = DiagnosticoFuncionalCreateForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            nombre = nombre.upper()
            id_diagnostico_etiologico = form.cleaned_data['id_diagnostico_etiologico']
            diagnosticoFuncionalRepo.create(
                nombre=nombre,
                id_diagnostico_etiologico=id_diagnostico_etiologico,
            )
            return redirect('diagnosticos_funcionales_list')
        else:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoFuncionalUpdate(View):

    def get(self, request, id):
        diagnostico_funcional = diagnosticoFuncionalRepo.filter_by_id(id=id)
        if diagnostico_funcional is None:
            messages.error(request, 'No se encontró el diagnóstico funcional.')
            return redirect('diagnosticos_funcionales_list')
        form = DiagnosticoFuncionalCreateForm(instance=diagnostico_funcional)
        return render(
            request,
            'diagnosticos/funcionales/update.html',
            dict(
                form=form,
                diagnostico=diagnostico_funcional,
            )
        )

    def post(self, request, id):
        diagnostico_funcional = diagnosticoFuncionalRepo.filter_by_id(id=id)
        if diagnostico_funcional is None:
            messages.error(request, 'No se encontró el diagnóstico funcional.')
            return redirect('diagnosticos_funcionales_list')
        form = DiagnosticoFuncionalCreateForm(request.POST, instance=diagnostico_funcional)
        if form.is_valid():
            diagnosticoFuncionalRepo.update(
                diagnostico_funcional=diagnostico_funcional,
                nombre=form.cleaned_data['nombre'].upper(),
                id_diagnostico_etiologico=form.cleaned_data['id_diagnostico_etiologico'],
            )
            messages.success(request, 'Diagnóstico funcional actualizado correctamente.')
            return redirect('diagnosticos_funcionales_list')
        return render(
            request,
            'diagnosticos/funcionales/update.html',
            dict(
                form=form,
                diagnostico=diagnostico_funcional,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticoFuncionalDelete(View):

    def get(self, request, id):
        diagnostico_funcional = diagnosticoFuncionalRepo.filter_by_id(id=id)
        if diagnostico_funcional is None:
            messages.error(request, 'No se encontró el diagnóstico funcional.')
            return redirect('diagnosticos_funcionales_list')

        if diagnosticoFuncionalRepo.has_alta_funcional_relation(diagnostico_funcional):
            messages.error(
                request,
                'No se puede eliminar porque tiene una relación activa. Primero debe eliminar el diagnóstico relacionado.'
            )
            return redirect('diagnosticos_funcionales_list')

        diagnosticoFuncionalRepo.delete(diagnostico_funcional=diagnostico_funcional)
        messages.success(request, 'Diagnóstico funcional eliminado correctamente.')
        return redirect('diagnosticos_funcionales_list')
