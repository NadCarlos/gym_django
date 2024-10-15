from django.views import View
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from administracion.filters import ProfesionalFilter

from administracion.repositories.profesional import ProfesionalRepository


profesionalRepo = ProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalList(View):
    template_name = 'profesional/list.html'
    context_object_name = 'profesional'

    def get(self, request):

        filterset = ProfesionalFilter(request.GET, profesionalRepo.filter_by_activo())
        
        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        # Obtener el queryset filtrado
        profesionales = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            profesionales = filterset.qs.order_by(ordering)

        return render(
            request,
            self.template_name,
            dict(
                profesionales=profesionales,
                form=filterset.form,
                ordering=ordering,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalDetail(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        return render(
            request,
            'profesional/detail.html',
            dict(
                profesional=profesional,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalDelete(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        profesionalRepo.delete_by_activo(profesional=profesional)
        return redirect('profesional_list')