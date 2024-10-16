from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import TratamientoProfesionalCreateForm

from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository


profesionalRepo = ProfesionalRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoProfesionalList(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        profesional_id = profesional.id
        tratamientos_profesional = tratamientoProfesionalRepo.filter_by_id_profesional_all(id_profesional=profesional_id)
        return render(
            request,
            'tratamiento_profesional/list.html',
            dict(
                profesional=profesional,
                tratamientos_profesional=tratamientos_profesional
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoProfesionalCreate(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        form = TratamientoProfesionalCreateForm(initial = {'id_profesional': profesional.id})
        return render(
            request,
            'tratamiento_profesional/create.html',
            dict(
                form=form
            )
        )

    def post(self, request, id, *args, **kwargs):
        form = TratamientoProfesionalCreateForm(request.POST)
        try:
            if form.is_valid():
                nuevo_tratamiento_profesional = tratamientoProfesionalRepo.create(
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    tratamiento=form.cleaned_data['id_tratamiento'],
                    profesional=form.cleaned_data['id_profesional'],
                )
                return redirect('profesional_detail', nuevo_tratamiento_profesional.id_profesional.id)
        except:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
class TratamientoProfesionalDelete(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, id):
        tratamiento_profesional = tratamientoProfesionalRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        tratamientoProfesionalRepo.delete_by_activo(profesional_tratamiento=tratamiento_profesional)
        return redirect('tratamiento_profesional_list', tratamiento_profesional.id_profesional.id)