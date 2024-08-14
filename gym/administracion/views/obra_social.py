from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from administracion.forms import (
    ObraSocialForm,
)

from administracion.repositories.obra_social import ObraSocialRepository


obraSocialRepo = ObraSocialRepository()


class ObraSocialList(View):

    @method_decorator(permission_required(perm='gym.obras_sociales', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        obras_sociales = obraSocialRepo.get_all()
        return render(
            request,
            'obra_social/list.html',
            dict(
                obras_sociales=obras_sociales
            )
        )
    

class ObraSocialCreate(View):

    @method_decorator(permission_required(perm='gym.obra_social_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def get(self, request):
        form = ObraSocialForm()
        return render(
            request,
            'obra_social/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(permission_required(perm='gym.obra_social_create', login_url='error', raise_exception=True))
    @method_decorator(login_required(login_url='error'))
    def post(self, request):
        form = ObraSocialForm(request.POST)
        try:
            if form.is_valid():
                obraSocialRepo.create(
                    nombre=form.cleaned_data['nombre'],
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('obras_sociales')
        except:
            return redirect('error')