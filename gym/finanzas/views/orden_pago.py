import locale
import json

from django.views import View
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages

from utils.permissions import es_admin_o_finanzas

from finanzas.forms import (
    OrdenPagoCreateForm,
)

from finanzas.filters import OrdenesPagoFilter

from finanzas.repositories.facturas import FacturaRepository
from finanzas.repositories.orden_pago import OrdenPagoRepository
from finanzas.repositories.detalle_orden_pago import DetalleOrdenRepo
from finanzas.repositories.descuentos import DescuentoRepository
from finanzas.repositories.conceptos import ConceptoRepository
from finanzas.repositories.beneficiarios import BeneficiarioRepository


facturaRepo = FacturaRepository()
ordenPagoRepo = OrdenPagoRepository()
detalleOrdenRepo = DetalleOrdenRepo()
descuentoRepo = DescuentoRepository()
conceptoRepo = ConceptoRepository()
beneficiarioRepo = BeneficiarioRepository()

locale.setlocale(locale.LC_ALL, '')


@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
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


@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
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
        from_list = False
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas_ids = request.POST.get('facturas')
        facturas_ids = str(facturas_ids)
        if facturas_ids != "":
            facturas_ids = json.loads(facturas_ids)
        conceptos = request.POST.get('conceptos')
        conceptos = str(conceptos)
        if conceptos != "":
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
            importe = float(concepto["importe"])
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

        return redirect('detail', id, from_list)


@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoEdit(View):

    def get(self, request, id, from_list):
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas = facturaRepo.filter_by_beneficiario_id(id_beneficiario=orden.id_beneficiario)
        conceptos = conceptoRepo.get_all()

        ordenes_selected = detalleOrdenRepo.filter_by_orden_id(orden_id=id)
        facturas_selected = []
        for orden_selected in ordenes_selected:
            fact = orden_selected.id_factura
            fact = json.dumps(
                    {
                        "id": fact.id,
                        "numero": fact.numero,
                        "importe": float(fact.importe),
                        "fecha": str(fact.fecha),
                        "pto_vta": fact.pto_vta,
                    }
                )
            facturas_selected.append(fact)

        descuentos_selected = descuentoRepo.filter_by_orden_id(orden_id=orden.id)
        descuentos_selected_json = []
        for d in descuentos_selected:
            desc_sel = json.dumps(
                    {
                        "id": d.id,
                        "id_concepto": d.id_concepto.nombre,
                        "importe": float(d.importe),
                        "observaciones": d.observaciones,
                    }
                )
            descuentos_selected_json.append(desc_sel)

        facturas_selected_json = mark_safe(json.dumps(facturas_selected, ensure_ascii=False))
        descuentos_selected_json = mark_safe(json.dumps(descuentos_selected_json, ensure_ascii=False))

        for factura in facturas:
            factura.importe = locale.currency(factura.importe, grouping=True)
            factura.pto_vta = factura.pto_vta.zfill(4)

        return render(
            request,
            'orden_pago/edit.html',
            dict(
                orden = orden,
                facturas = facturas,
                conceptos = conceptos,
                facturas_selected_json = facturas_selected_json,
                descuentos_selected_json = descuentos_selected_json,
                from_list = from_list,
            )
        )

    def post(self, request, id, from_list):
        orden = ordenPagoRepo.filter_by_id(id=id)
        facturas_ids = request.POST.get('facturas')
        facturas_ids = str(facturas_ids)
        facturas_ids = json.loads(facturas_ids)

        detalle_orden_old = detalleOrdenRepo.filter_by_orden_id(orden_id=orden.id)
        det_ord_fact_list = [] #ids
        det_ord_list = [] # noids
        for det_ord in detalle_orden_old:
            det_ord_list.append(det_ord)
            det_ord_fact_list.append(det_ord.id_factura.id)

        facturasTotal = 0

        # valido si existe o no en la antiguas y si no esta la creamo viteh
        for factura_id in facturas_ids:
            if factura_id not in det_ord_fact_list:
                factura = facturaRepo.filter_by_id(id=factura_id)
                factura_importe = float(factura.importe)
                facturasTotal = facturasTotal + factura_importe
                detalleOrdenRepo.create(
                    importe=factura.importe,
                    id_ordenpago=orden,
                    id_factura=factura,
                )

        
        for factura_id in det_ord_fact_list:
            if factura_id not in facturas_ids:
                factura = facturaRepo.filter_by_id(id=factura_id)
                detalle_orden = detalleOrdenRepo.filter_by_orden_pago_and_factura_id(factura_id=factura.id, orden_id=orden.id)
                detalleOrdenRepo.update_activo(
                    detalle_orden = detalle_orden,
                    activo=False,
                )
            else:
                factura = facturaRepo.filter_by_id(id=factura_id)
                factura_importe = float(factura.importe)
                facturasTotal = facturasTotal + factura_importe
        
        #conceptos existentes
        descuentos_list_old = descuentoRepo.filter_by_orden_id(orden_id=orden.id)
        descuentos_list_old_ids = []
        for dto in descuentos_list_old:
            dto_id = int(dto.id)
            descuentos_list_old_ids.append(dto_id)

        descuentosTotal = 0

        descuentos_new = request.POST.get('conceptos_old')
        descuentos_new = str(descuentos_new)
        if descuentos_new != "":
            descuentos_new = json.loads(descuentos_new)
            descuentos_new_ids = []
            for dto_new in descuentos_new:
                dto_id = int(dto_new["id"])
                descuentos_new_ids.append(dto_id)

            for descuento_id in descuentos_list_old_ids:
                if descuento_id not in descuentos_new_ids:
                    descuento_a_borrar = descuentoRepo.filter_by_id(id=descuento_id)
                    descuentoRepo.update_activo(
                        descuento=descuento_a_borrar,
                        activo=False,
                    )
                else:
                    descuento_existente = descuentoRepo.filter_by_id(id=descuento_id)
                    descuento_existente_importe = float(descuento_existente.importe)
                    descuentosTotal = descuentosTotal + descuento_existente_importe

        elif not descuentos_new:
            for concepto_id in descuentos_list_old_ids:
                descuento_a_borrar = descuentoRepo.filter_by_id(id=concepto_id)
                descuentoRepo.update_activo(
                    descuento=descuento_a_borrar,
                    activo=False,
                )

        #conceptos nuevos
        conceptos = request.POST.get('conceptos')
        conceptos = str(conceptos)
        conceptos = json.loads(conceptos)
        for concepto in conceptos:
            importe = float(concepto["importe"])
            observaciones = concepto["observaciones"]

            if concepto["id"]:
                if observaciones == "":
                    observaciones = "Sin Observaciones"
                if concepto["id"] == "NEW":
                    nuevo_concepto = conceptoRepo.create(nombre=concepto["nombre"])
                    dto_importe = float(importe)
                    descuentosTotal = descuentosTotal + dto_importe
                    descuento = descuentoRepo.create(
                        id_ordenpago = orden,
                        id_concepto = nuevo_concepto,
                        importe = importe,
                        observaciones = observaciones,
                    )
                else:
                    concepto_existente = conceptoRepo.filter_by_id(id=concepto["id"])
                    dto_importe = float(importe)
                    descuentosTotal = descuentosTotal + dto_importe
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

        if from_list == "True":
            messages.success(request, "Orden de pago creada correctamente desde la lista.")

        return redirect('detail', id, from_list)


@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoDetail(View):

    def get(self, request, id, from_list):
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
                from_list = from_list,
            )
        )
    

@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenesPagoList(View):
    context_object_name = 'ordenes'

    def get(self, request):
        from_list = False
        """if request.GET.get('fecha_after') is None:
            hoy = datetime.today()
            hace_10_dias = hoy - timedelta(days=10)

            # Instanciar el filtro con los datos enviados por el formulario
            filterset = OrdenesPagoFilter(
                request.GET, queryset=ordenPagoRepo.filter_by_dates(start_date=hace_10_dias, end_date=hoy)
            )
        else:
            filterset = OrdenesPagoFilter(request.GET, queryset=ordenPagoRepo.filter_by_activo())"""
        
        filterset = OrdenesPagoFilter(request.GET, queryset=ordenPagoRepo.filter_by_activo())
        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', '-fecha')

        # Obtener el queryset filtrado
        ordenes = filterset.qs

        # Aplicar el ordenamiento si existe
        if ordering:
            ordenes = ordenes.order_by(ordering)

        ordenes_count = ordenes.count()

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
                ordenes_count=ordenes_count,
                form=filterset.form,
                ordering=ordering,
                total=total,
                from_list=from_list,
            )
        )
    

@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoDelete(View):

    def get(self, request, id, from_list):
        print(from_list)
        orden = ordenPagoRepo.filter_by_id(id=id)
        detalles = detalleOrdenRepo.filter_by_orden_id(orden_id=orden.id)
        for detalle in detalles:
            detalleOrdenRepo.delete_by_activo(detalle_orden=detalle)
        #No elimino, cambio el campo activo a False
        ordenPagoRepo.delete_by_activo(orden=orden)
        if from_list == "False":
            return redirect('orden_pago_list')
        elif from_list == "True":
            return redirect('list')
    

@method_decorator(user_passes_test(es_admin_o_finanzas, login_url='login'), name='dispatch')
@method_decorator(login_required(login_url='login'), name='dispatch')
class OrdenPagoCreateFromList(View):

    def post(self, request):
        from_list = True
        facturas_ids = request.POST.getlist('facturas[]')
        numero = request.POST.get('numero')
        fecha = request.POST.get('fecha')
        beneficiario = beneficiarioRepo.filter_by_nombre(nombre=request.POST.get('beneficiario'))
        
        orden = ordenPagoRepo.create(
                    id_usuario=request.user,
                    fecha=fecha,
                    numero=numero,
                    id_beneficiario=beneficiario,
                    total=0,
                )
        
        facturasTotal = 0
        for factura_id in facturas_ids:
            factura = facturaRepo.filter_by_id(id=factura_id)
            facturasTotal = facturasTotal + factura.importe
            detalleOrdenRepo.create(
                importe=factura.importe,
                id_ordenpago=orden,
                id_factura=factura,
            )
        
        ordenPagoRepo.update_total(
            orden_pago=orden,
            total=facturasTotal,
        )

        return redirect('orden_pago_edit', orden.id, from_list)