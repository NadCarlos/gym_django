from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.forms import (
    BeneficiarioUpdateForm,
)

from finanzas.repositories.beneficiarios import BeneficiarioRepository


beneficiarioRepo = BeneficiarioRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class BeneficiariosList(View):

    def get(self, request):
        beneficiarios = beneficiarioRepo.filter_by_activo()

        return render(
            request,
            'beneficiarios/list.html',
            dict(
                beneficiarios=beneficiarios,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
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