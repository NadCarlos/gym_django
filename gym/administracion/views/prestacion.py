from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from administracion.forms import (
    PrestacionForm,
)

from administracion.repositories.prestacion import PrestacionRepository


prestacionRepo = PrestacionRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PrestacionList(View):

    def get(self, request, area):
        if area == 1:
            base_template = "home/base.html"
        elif area == 2:
            base_template = "inicio/base.html"
        prestaciones = prestacionRepo.filter_by_activo()
        prestaciones_count = prestaciones.count()
        return render(
            request,
            'prestacion/list.html',
            dict(
                prestaciones_count=prestaciones_count,
                prestaciones=prestaciones,
                area=area,
                base_template=base_template,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PrestacionCreate(View):

    def get(self, request, area):
        if area == 1:
            base_template = "home/base.html"
        elif area == 2:
            base_template = "inicio/base.html"
        form = PrestacionForm()
        return render(
            request,
            'prestacion/create.html',
            dict(
                form=form,
                area=area,
                base_template=base_template,
            )
        )
    
    def post(self, request, area):
        form = PrestacionForm(request.POST)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                prestacionRepo.create(
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('prestaciones', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PrestacionUpdate(View):

    def get(self, request, id, area, *args, **kwargs):
        if area == 1:
            base_template = "home/base.html"
        elif area == 2:
            base_template = "inicio/base.html"
        prestacion = prestacionRepo.get_by_id(id=id)
        form = PrestacionForm(instance=prestacion)
        return render(
            request,
            'prestacion/update.html',
            dict(
                form=form,
                area=area,
                base_template=base_template,
            )
        )

    def post(self, request, id, area):
        form = PrestacionForm(request.POST)
        prestacion = prestacionRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                prestacionRepo.update(
                    prestacion=prestacion,
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('prestaciones', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class PrestacionDelete(View):

    def get(self, request, id, area):
        prestacion = prestacionRepo.get_by_id(id=id)
        prestacionRepo.delete_by_activo(prestacion=prestacion)
        return redirect ('prestaciones', area)