from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from rehabilitacion.forms import(
    TipoDiscapacidadCreateForm,
)


from rehabilitacion.repositories.tipo_discapacidad import TipoDiscapacidadRepository
tipoDiscapacidadRepo = TipoDiscapacidadRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
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
            tipoDiscapacidadRepo.create(
                nombre=nombre,
            )
            return redirect('tipo_discapacidad_list')
        else:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TipoDiscapacidadUpdate(View):

    def get(self, request, id):
        tipo_discapacidad = tipoDiscapacidadRepo.filter_by_id(id=id)
        if tipo_discapacidad is None:
            messages.error(request, 'No se encontró el tipo de discapacidad.')
            return redirect('tipo_discapacidad_list')
        form = TipoDiscapacidadCreateForm(instance=tipo_discapacidad)
        return render(
            request,
            'diagnosticos/tipos_discapacidad/update.html',
            dict(
                form=form,
                tipo_discapacidad=tipo_discapacidad,
            )
        )

    def post(self, request, id):
        tipo_discapacidad = tipoDiscapacidadRepo.filter_by_id(id=id)
        if tipo_discapacidad is None:
            messages.error(request, 'No se encontró el tipo de discapacidad.')
            return redirect('tipo_discapacidad_list')
        form = TipoDiscapacidadCreateForm(request.POST, instance=tipo_discapacidad)
        if form.is_valid():
            nombre = form.cleaned_data['nombre'].upper()
            tipoDiscapacidadRepo.update(
                tipo_discapacidad=tipo_discapacidad,
                nombre=nombre,
            )
            messages.success(request, 'Tipo de discapacidad actualizado correctamente.')
            return redirect('tipo_discapacidad_list')
        return render(
            request,
            'diagnosticos/tipos_discapacidad/update.html',
            dict(
                form=form,
                tipo_discapacidad=tipo_discapacidad,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TipoDiscapacidadDelete(View):

    def get(self, request, id):
        tipo_discapacidad = tipoDiscapacidadRepo.filter_by_id(id=id)
        if tipo_discapacidad is None:
            messages.error(request, 'No se encontró el tipo de discapacidad.')
            return redirect('tipo_discapacidad_list')

        if tipoDiscapacidadRepo.has_alta_relation(tipo_discapacidad):
            messages.error(
                request,
                'No se puede eliminar porque tiene una relación activa con un alta. '
                'Primero debe quitar esa relación.'
            )
            return redirect('tipo_discapacidad_list')

        tipoDiscapacidadRepo.delete(tipo_discapacidad=tipo_discapacidad)
        messages.success(request, 'Tipo de discapacidad eliminado correctamente.')
        return redirect('tipo_discapacidad_list')
