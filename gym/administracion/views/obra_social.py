from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from administracion.forms import (
    ObraSocialForm,
)

from administracion.repositories.obra_social import ObraSocialRepository


obraSocialRepo = ObraSocialRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class ObraSocialList(View):

    def get(self, request, area):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        obras_sociales = obraSocialRepo.filter_by_activo()
        obras_sociales_count = obras_sociales.count()
        return render(
            request,
            'obra_social/list.html',
            dict(
                obras_sociales_count=obras_sociales_count,
                obras_sociales=obras_sociales,
                area=area,
                base_template=base_template,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class ObraSocialCreate(View):

    def get(self, request, area):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        form = ObraSocialForm()
        return render(
            request,
            'obra_social/create.html',
            dict(
                form=form,
                area=area,
                base_template=base_template,
            )
        )
    
    def post(self, request, area):
        form = ObraSocialForm(request.POST)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                obraSocialRepo.create(
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('obras_sociales', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class ObraSocialUpdate(View):

    def get(self, request, id, area, *args, **kwargs):
        if area == 1:
            base_template="home/base.html"
        elif area == 2:
            base_template="inicio/base.html"
        obra_social = obraSocialRepo.get_by_id(id=id)
        form = ObraSocialForm(instance=obra_social)
        return render(
            request,
            'obra_social/update.html',
            dict(
                form=form,
                area=area,
                base_template=base_template,
            )
        )
    
    def post(self, request, id, area):
        form = ObraSocialForm(request.POST)
        obra_social = obraSocialRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                obraSocialRepo.update(
                    obra_social=obra_social,
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    )
                return redirect('obras_sociales', area)
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Gimnasio", "Rehabilitacion"), name="dispatch")
class ObraSocialDelete(View):

    def get(self, request, id, area):
        obra_social = obraSocialRepo.get_by_id(id=id)
        obraSocialRepo.delete_by_activo(obra_social=obra_social)
        return redirect ('obras_sociales', area)