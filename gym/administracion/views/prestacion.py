from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PrestacionForm,
)

from administracion.repositories.prestacion import PrestacionRepository


prestacionRepo = PrestacionRepository()


class PrestacionList(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        prestaciones = prestacionRepo.filter_by_activo()
        return render(
            request,
            'prestacion/list.html',
            dict(
                prestaciones=prestaciones
            )
        )
    

class PrestacionCreate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = PrestacionForm()
        return render(
            request,
            'prestacion/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request):
        form = PrestacionForm(request.POST)
        try:
            if form.is_valid():
                prestacionRepo.create(
                    nombre=form.cleaned_data['nombre'],
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('prestaciones')
        except:
            return redirect('error')
        

class PrestacionUpdate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id, *args, **kwargs):

        prestacion = prestacionRepo.get_by_id(id=id)
        form = PrestacionForm(instance=prestacion)
        return render(
            request,
            'prestacion/update.html',
            dict(
                form=form,
            )
        )
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, id):
        form = PrestacionForm(request.POST)
        prestacion = prestacionRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                prestacionRepo.update(
                    prestacion=prestacion,
                    nombre=form.cleaned_data['nombre'],
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('prestaciones')
        except:
            return redirect('error')
        

class PrestacionDelete(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        prestacion = prestacionRepo.get_by_id(id=id)
        prestacionRepo.delete_by_activo(prestacion=prestacion)
        return redirect ('prestaciones')