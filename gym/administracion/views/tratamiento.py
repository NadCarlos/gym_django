from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    TratamientoForm,
)

from administracion.repositories.tratamiento import TratamientoRepository


tratamientoRepo = TratamientoRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoList(View):

    def get(self, request, area):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        tratamientos = tratamientoRepo.filter_by_activo()
        tratamientos_count = tratamientos.count()
        return render(
            request,
            'tratamiento/list.html',
            dict(
                tratamientos=tratamientos,
                tratamientos_count=tratamientos_count,
                base_template=base_template,
                area=area,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoCreate(View):

    def get(self, request, area):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        form = TratamientoForm()
        return render(
            request,
            'tratamiento/create.html',
            dict(
                form=form,
                base_template=base_template,
            )
        )
    
    def post(self, request, area):
        form = TratamientoForm(request.POST)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                tratamientoRepo.create(
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('tratamientos', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoUpdate(View):

    def get(self, request, id, area, *args, **kwargs):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        tratamiento = tratamientoRepo.get_by_id(id=id)
        form = TratamientoForm(instance=tratamiento)
        return render(
            request,
            'tratamiento/update.html',
            dict(
                form=form,
                base_template=base_template,
            )
        )
    
    def post(self, request, id, area):
        form = TratamientoForm(request.POST)
        tratamiento = tratamientoRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                tratamientoRepo.update(
                    tratamiento=tratamiento,
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('tratamientos', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoDelete(View):

    def get(self, request, id, area):
        tratamiento = tratamientoRepo.get_by_id(id=id)
        tratamientoRepo.delete_by_activo(tratamiento=tratamiento)
        return redirect ('tratamientos', area)