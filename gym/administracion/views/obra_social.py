from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import (
    ObraSocialForm,
)

from administracion.repositories.obra_social import ObraSocialRepository


obraSocialRepo = ObraSocialRepository()


class ObraSocialList(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        obras_sociales = obraSocialRepo.filter_by_activo()
        return render(
            request,
            'obra_social/list.html',
            dict(
                obras_sociales=obras_sociales
            )
        )
    

class ObraSocialCreate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = ObraSocialForm()
        return render(
            request,
            'obra_social/create.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(login_required(login_url='login'))
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
        

class ObraSocialUpdate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id, *args, **kwargs):

        obra_social = obraSocialRepo.get_by_id(id=id)
        form = ObraSocialForm(instance=obra_social)
        return render(
            request,
            'obra_social/update.html',
            dict(
                form=form,
            )
        )
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, id):
        form = ObraSocialForm(request.POST)
        obra_social = obraSocialRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                obraSocialRepo.update(
                    obra_social=obra_social,
                    nombre=form.cleaned_data['nombre'],
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('obras_sociales')
        except:
            return redirect('error')
        

class ObraSocialDelete(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        obra_social = obraSocialRepo.get_by_id(id=id)
        obraSocialRepo.delete_by_activo(obra_social=obra_social)
        return redirect ('obras_sociales')