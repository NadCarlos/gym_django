import pandas # type: ignore

from datetime import datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.repositories.beneficiarios import BeneficiarioRepository
from finanzas.repositories.facturas import FacturaRepository


beneficiarioRepo = BeneficiarioRepository()
facturaRepo = FacturaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class CargaView(View):

    def get(self, request):
        return render(
            request,
            'libro_ventas/carga.html',
        )
    
    def post(self, request):
        file = request.FILES['file']
        excel = pandas.read_excel(file)
        cleaned_data = []
        for fila in excel.values:
            if isinstance(fila[0], datetime):
                cleaned_data.append(fila)

        # [0]=Fecha,[1]=Tipo,[2]=pto_vta,[3]=Nro,[4]=Nombre,[5]=Cuit,[6]=Importe
        for data in cleaned_data:
            beneficiarioExist = beneficiarioRepo.filter_by_numero_cuit(numero_cuit=data[5])
            if beneficiarioExist is None:
                nuevoBeneficiario = beneficiarioRepo.create(
                    nombre=data[4],
                    numero_cuit=data[5],
                )

                beneficiarioExist = nuevoBeneficiario

            importe = float(data[6])
            facturaRepo.create(
                tipo=data[1],
                pto_vta=data[2],
                numero=data[3],
                fecha=data[0],
                importe=importe,
                id_beneficiario=beneficiarioExist,
            )
            

        return render(
            request,
            'libro_ventas/list.html',
            dict(
                cleaned_data=cleaned_data,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class GuardarCarga(View):

    def get(self, request):
        print(request.POST)