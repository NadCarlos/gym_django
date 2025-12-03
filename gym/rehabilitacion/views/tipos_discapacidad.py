from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from rehabilitacion.forms import(
    TipoDiscapacidadCreateForm,
)


from rehabilitacion.repositories.tipo_discapacidad import TipoDiscapacidadRepository


tipoDiscapacidadRepo = TipoDiscapacidadRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class TipoDiscapacidadList(View):

    def get(self, request):
        tipos_discapacidad = tipoDiscapacidadRepo.get_all()
        return render(
            request,
            'diagnosticos/tipos_discapacidad/list.html',
            dict(
                tipos_discapacidad = tipos_discapacidad,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class TipoDiscapacidadCreate(View):

    def get(self, request):
        form = TipoDiscapacidadCreateForm()
        return render(
            request,
            'diagnosticos/tipos_discapacidad/create.html',
            dict(
                form=form,
            )
        )
    
    def post(self, request):
        form = TipoDiscapacidadCreateForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            nombre = nombre.upper()
            rehabilitacion_nueva = tipoDiscapacidadRepo.create(
                nombre=nombre,
            )
            return redirect('tipo_discapacidad_list')
        else:
            return redirect('error')