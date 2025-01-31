import pandas
import locale
from datetime import datetime, timedelta

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.forms import BeneficiarioUpdateForm

from finanzas.filters import FacturasFilter

from finanzas.repositories.beneficiarios import BeneficiarioRepository
from finanzas.repositories.facturas import FacturaRepository


beneficiarioRepo = BeneficiarioRepository()
facturaRepo = FacturaRepository()

locale.setlocale(locale.LC_ALL, '')


@method_decorator(login_required(login_url='login'), name='dispatch')
class Index(View):

    def get(self, request):
        return render(
            request,
            'libro_ventas/index.html',
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class CargaView(View):

    def get(self, request):
        return render(
            request,
            'libro_ventas/carga.html',
        )
    
    def post(self, request):
        try:
            file = request.FILES['file']
        except:
            return redirect('error')
        excel = pandas.read_excel(file)
        cleaned_data = []
        for fila in excel.values:
            if isinstance(fila[0], datetime):
                cleaned_data.append(fila)

        # [0]=Fecha,[1]=Tipo,[2]=pto_vta,[3]=Nro,[4]=Nombre,[5]=Cuit,[6]=Importe
        for data in cleaned_data:
            facturaExist = facturaRepo.filter_by_numero_fact(fact_numero=data[3], pto_vta=data[2])
            if facturaExist is None:
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
            else:
                pass

        return redirect('list')


@method_decorator(login_required(login_url='login'), name='dispatch')
class FacturasList(View):
    context_object_name = 'facturas'

    def get(self, request):
        if request.GET.get('fecha_after') is None:
            hoy = datetime.today()
            hace_30_dias = hoy - timedelta(days=10)

            # Instanciar el filtro con los datos enviados por el formulario
            filterset = FacturasFilter(request.GET, queryset=facturaRepo.filter_by_dates(start_date=hace_30_dias,end_date=hoy))
        else:
            filterset = FacturasFilter(request.GET, queryset=facturaRepo.get_all())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')
        # Obtener el queryset filtrado
        facturas = filterset.qs
        # Aplicar el ordenamiento si existe
        if ordering:
            facturas = facturas.order_by(ordering)

        total = 0
        for factura in facturas:
            total += factura.importe
            factura.importe = locale.currency(factura.importe, grouping=True)
            factura.pto_vta = factura.pto_vta.zfill(4)
            factura.numero = factura.numero.zfill(8)

        total = locale.currency(total, grouping=True)

        return render(
            request,
            'libro_ventas/list.html',
            dict(
                facturas=facturas,
                form=filterset.form,
                ordering=ordering,
                total=total,
            )
        )
    

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