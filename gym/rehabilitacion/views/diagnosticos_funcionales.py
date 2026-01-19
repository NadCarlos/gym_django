from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
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
            diagnostico_funcional_nuevo = diagnosticoFuncionalRepo.create(
                nombre=nombre,
                id_diagnostico_etiologico=id_diagnostico_etiologico,
            )
            return redirect('diagnosticos_funcionales_list')
        else:
            return redirect('error')