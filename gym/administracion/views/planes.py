from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from administracion.forms import PlanForm, PlanUpdateForm

from administracion.repositories.planes import PlanRepository


planRepo = PlanRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class PlanesList(View):

    def get(self, request):
        planes = planRepo.filter_by_activo()
        planes_count = planes.count()

        return render(
            request,
            'planes/list.html',
            dict(
                planes=planes,
                planes_count=planes_count,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class PlanCreate(View):

    def get(self, request):
        form = PlanForm(initial = {'id_usuario': request.user})
        return render(
            request,
            'planes/create.html',
            dict(
                form=form
            )
        )

    def post(self, request):
        form = PlanForm(request.POST)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                planRepo.create(
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    valor=form.cleaned_data['valor'],
                    id_usuario=form.cleaned_data['id_usuario'],
                    )
                return redirect('planes_list')
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class PlanUpdate(View):

    def get(self, request, id):
        plan = planRepo.get_by_id(id=id)
        form = PlanUpdateForm(instance=plan)
        return render(
            request,
            'planes/create.html',
            dict(
                form=form
            )
        )

    def post(self, request, id):
        form = PlanUpdateForm(request.POST)
        plan = planRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre=form.cleaned_data['nombre']
                nombre=nombre.upper()
                planRepo.update(
                    plan=plan,
                    nombre=nombre,
                    descripcion=form.cleaned_data['descripcion'],
                    valor=form.cleaned_data['valor'],
                    )
                return redirect('planes_list')
        except:
            return redirect('error')
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class PlanDelete(View):

    def get(self, request, id):
        plan = planRepo.get_by_id(id=id)
        planRepo.delete_by_activo(plan=plan)
        return redirect ('planes_list')