from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas


from finanzas.forms import (
    BeneficiarioUpdateForm,
)

from finanzas.filters import BeneficiarioFilter

from finanzas.repositories.beneficiarios import BeneficiarioRepository


beneficiarioRepo = BeneficiarioRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class BeneficiariosList(View):

    def get(self, request):
        filterset = BeneficiarioFilter(request.GET, queryset=beneficiarioRepo.filter_by_activo())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering')
        # Obtener el queryset filtrado
        beneficiarios = filterset.qs
        # Aplicar el ordenamiento si existe
        if ordering:
            beneficiarios = beneficiarios.order_by(ordering)

        beneficiarios_count = beneficiarios.count()

        return render(
            request,
            'beneficiarios/list.html',
            dict(
                beneficiarios=beneficiarios,
                beneficiarios_count=beneficiarios_count,
                form=filterset.form,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class BeneficiarioUpdate(View):

    def get(self, request, id):
        beneficiario = beneficiarioRepo.get_by_id(id=id)
        form = BeneficiarioUpdateForm(instance=beneficiario)

        return render(
            request,
            'beneficiarios/update.html',
            dict(
                beneficiario=beneficiario,
                form=form,
            )
        )
    
    def post(self, request, id):
        form = BeneficiarioUpdateForm(request.POST)
        beneficiario = beneficiarioRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                beneficiarioRepo.update(
                    beneficiario=beneficiario,
                    nombre=form.cleaned_data['nombre'],
                    numero_cuit=form.cleaned_data['numero_cuit'],
                )
                return redirect('beneficiarios_list')
        except:
            return redirect('error')