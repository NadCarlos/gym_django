import pandas
import locale
from datetime import datetime, timedelta

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.forms import (
    BeneficiarioUpdateForm,
    OrdenPagoCreateForm,
    DetalleOrdenPagoCreateForm,
    DescuentoOrdenPagoCreateForm
)

from finanzas.filters import FacturasFilter

from finanzas.repositories.beneficiarios import BeneficiarioRepository
from finanzas.repositories.facturas import FacturaRepository
from finanzas.repositories.orden_pago import OrdenPagoRepository
from finanzas.repositories.detalle_orden_pago import DetalleOrdenRepo
from finanzas.repositories.descuentos import DescuentoRepository
from finanzas.repositories.conceptos import ConceptoRepository


beneficiarioRepo = BeneficiarioRepository()
facturaRepo = FacturaRepository()
ordenPagoRepo = OrdenPagoRepository()
detalleOrdenRepo = DetalleOrdenRepo()
descuentoRepo = DescuentoRepository()
conceptoRepo = ConceptoRepository()

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
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoCreate(View):

    def get(self, request):
        form = OrdenPagoCreateForm(initial = {'id_usuario': request.user,})

        return render(
            request,
            'orden_pago/create.html',
            dict(
                form = form,
            )
        )
    
    def post(self, request):
        form = OrdenPagoCreateForm(request.POST)
        if form.is_valid():
                orden = ordenPagoRepo.create(
                    id_usuario=form.cleaned_data['id_usuario'],
                    fecha=form.cleaned_data['fecha'],
                    numero=form.cleaned_data['numero'],
                    id_beneficiario=form.cleaned_data['id_beneficiario'],
                    total=form.cleaned_data['total'],
                )
                return redirect('orden_pago_populate', orden.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoPopulate(View):

    def get(self, request, id):
        orden = ordenPagoRepo.filter_by_id(id=id)
        form = DetalleOrdenPagoCreateForm(initial = {'id_ordenpago': orden.id}, id_beneficiario=orden.id_beneficiario.id)

        return render(
            request,
            'orden_pago/orden_pago_populate.html',
            dict(
                orden = orden,
                form = form,
            )
        )
    
    def post(self, request, id):
        orden = request.POST.get('id_ordenpago')
        orden = ordenPagoRepo.filter_by_id(id=id)
        importe = request.POST.get('importe')
        facturas_ids = request.POST.getlist('id_factura')

        for factura_id in facturas_ids:
            print(factura_id)
            factura = facturaRepo.filter_by_id(id=factura_id)
            detalleOrdenRepo.create(
                importe=importe,
                id_ordenpago=orden,
                id_factura=factura,
            )

        return redirect('orden_pago_descuento', orden.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoDescuento(View):

    def get(self, request, id):
        orden = ordenPagoRepo.filter_by_id(id=id)
        form = DescuentoOrdenPagoCreateForm(initial = {'id_ordenpago': orden.id})
        
        return render(
            request,
            'orden_pago/orden_pago_descuento.html',
            dict(
                orden = orden,
                form = form,
            )
        )
    
    def post(self, request, id):
        orden = request.POST.get('id_ordenpago')
        conceptos_ids = request.POST.getlist('id_concepto')
        print("request.POST", request.POST)
        print("Conceptos:",conceptos_ids)
        importe = request.POST.get('importe')
        observaciones = request.POST.get('observaciones')
        
        orden = ordenPagoRepo.filter_by_id(id=id)

        for concepto_id in conceptos_ids:
            concepto = conceptoRepo.filter_by_id(id=concepto_id)
            descuento = descuentoRepo.create(
                observaciones=observaciones,
                importe=importe,
                id_ordenpago=orden,
                id_concepto=concepto,
            )

        return redirect('detail', orden.id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoDetail(View):

    def get(self, request, id):
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas = detalleOrdenRepo.filter_by_orden_id(orden_id=orden.id)
        descuentos = descuentoRepo.filter_by_orden_id(orden_id=orden.id)

        return render(
            request,
            'orden_pago/detail.html',
            dict(
                orden=orden,
                facturas=facturas,
                descuentos=descuentos,
            )
        )