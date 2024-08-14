from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from administracion.forms import (
    PrestacionForm,
)

from administracion.repositories.prestacion import PrestacionRepository


prestacionRepo = PrestacionRepository()


class PrestacionList(View):

    @method_decorator(permission_required(perm='gym.prestaciones', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        prestaciones = prestacionRepo.get_all()
        return render(
            request,
            'prestacion/list.html',
            dict(
                prestaciones=prestaciones
            )
        )
    

class PrestacionCreate(View):

    @method_decorator(permission_required(perm='gym.prestacion_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        form = PrestacionForm()
        return render(
            request,
            'prestacion/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(permission_required(perm='gym.prestacion_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
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