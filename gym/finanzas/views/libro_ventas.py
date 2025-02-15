import pandas
import locale
import json
from datetime import datetime, timedelta

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.forms import (
    BeneficiarioUpdateForm,
    OrdenPagoCreateForm,
)

from finanzas.filters import FacturasFilter, OrdenesPagoFilter

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
            hace_30_dias = hoy - timedelta(days=100)

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
        form = OrdenPagoCreateForm(initial = {'id_usuario': request.user})

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
        facturas = facturaRepo.filter_by_beneficiario_id(id_beneficiario=orden.id_beneficiario)
        conceptos = conceptoRepo.get_all()

        for factura in facturas:
            factura.importe = locale.currency(factura.importe, grouping=True)
            factura.pto_vta = factura.pto_vta.zfill(4)

        return render(
            request,
            'orden_pago/orden_pago_populate.html',
            dict(
                orden = orden,
                facturas = facturas,
                conceptos = conceptos,
            )
        )
    
    def post(self, request, id):
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas_ids = request.POST.get('facturas')
        facturas_ids = str(facturas_ids)
        facturas_ids = json.loads(facturas_ids)
        conceptos = request.POST.get('conceptos')
        conceptos = str(conceptos)
        conceptos = json.loads(conceptos)

        facturasTotal = 0
        for factura_id in facturas_ids:
            factura = facturaRepo.filter_by_id(id=factura_id)
            facturasTotal = facturasTotal + factura.importe
            detalleOrdenRepo.create(
                importe=factura.importe,
                id_ordenpago=orden,
                id_factura=factura,
            )

        descuentosTotal = 0
        for concepto in conceptos:
            importe = int(concepto["importe"])
            observaciones = concepto["observaciones"]
            if observaciones == "":
                observaciones = "Sin Observaciones"
            if concepto["id"] == "NEW":
                nuevo_concepto = conceptoRepo.create(nombre=concepto["nombre"])
                descuento = descuentoRepo.create(
                    id_ordenpago = orden,
                    id_concepto = nuevo_concepto,
                    importe = importe,
                    observaciones = observaciones,
                )
            else:
                concepto_existente = conceptoRepo.filter_by_id(id=concepto["id"])
                descuento = descuentoRepo.create(
                    id_ordenpago = orden,
                    id_concepto = concepto_existente,
                    importe = importe,
                    observaciones = observaciones,
                )

        total = facturasTotal - descuentosTotal
        
        ordenPagoRepo.update_total(
            orden_pago=orden,
            total=total,
        )

        return redirect('detail', id)


@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoDetail(View):

    def get(self, request, id):
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas = detalleOrdenRepo.filter_by_orden_id(orden_id=orden.id)
        descuentos = descuentoRepo.filter_by_orden_id(orden_id=orden.id)

        facturasTotal = 0
        for factura in facturas:
            facturasTotal = facturasTotal + factura.id_factura.importe
            factura.id_factura.importe = locale.currency(factura.id_factura.importe, grouping=True)

        descuentosTotal = 0
        for descuento in descuentos:
            descuentosTotal = descuentosTotal + descuento.importe
            descuento.importe = locale.currency(descuento.importe, grouping=True)

        total = facturasTotal - descuentosTotal
        descuentosTotal = locale.currency(descuentosTotal, grouping=True)
        facturasTotal = locale.currency(facturasTotal, grouping=True)
        total = locale.currency(total, grouping=True)

        return render(
            request,
            'orden_pago/detail.html',
            dict(
                orden=orden,
                facturas=facturas,
                facturasTotal=facturasTotal,
                descuentos=descuentos,
                descuentosTotal=descuentosTotal,
                total = total,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenesPagoList(View):
    context_object_name = 'ordenes'

    def get(self, request):
        if request.GET.get('fecha_after') is None:
            hoy = datetime.today()
            hace_10_dias = hoy - timedelta(days=10)

            # Instanciar el filtro con los datos enviados por el formulario
            filterset = OrdenesPagoFilter(
                request.GET, queryset=ordenPagoRepo.filter_by_dates(start_date=hace_10_dias, end_date=hoy)
            )
        else:
            filterset = OrdenesPagoFilter(request.GET, queryset=ordenPagoRepo.filter_by_activo())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')

        # Obtener el queryset filtrado
        ordenes = filterset.qs

        # Aplicar el ordenamiento si existe
        if ordering:
            ordenes = ordenes.order_by(ordering)

        total = 0
        for orden in ordenes:
            total += orden.total
            orden.total = locale.currency(orden.total, grouping=True)
            orden.numero = orden.numero.zfill(8)

        total = locale.currency(total, grouping=True)

        return render(
            request,
            'orden_pago/list.html',
            dict(
                ordenes=ordenes,
                form=filterset.form,
                ordering=ordering,
                total=total,
            )
        )