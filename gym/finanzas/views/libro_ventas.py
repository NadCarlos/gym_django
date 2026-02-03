import pandas
import io
import locale
from datetime import datetime, timedelta

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, HttpResponse
from utils.decorators import requiere_areas


from finanzas.filters import FacturasFilter

from finanzas.repositories.beneficiarios import BeneficiarioRepository
from finanzas.repositories.facturas import FacturaRepository
from finanzas.repositories.detalle_orden_pago import DetalleOrdenRepo
from finanzas.repositories.orden_pago import OrdenPagoRepository
from finanzas.repositories.descuentos import DescuentoRepository
from administracion.repositories.paciente import PacienteRepository


beneficiarioRepo = BeneficiarioRepository()
facturaRepo = FacturaRepository()
detalleOrdenRepo = DetalleOrdenRepo()
ordenPagoRepo = OrdenPagoRepository()
descuentoRepo = DescuentoRepository()
pacienteRepo = PacienteRepository()

locale.setlocale(locale.LC_ALL, '')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class Index(View):

    def get(self, request):
        return render(
            request,
            'libro_ventas/index.html',
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
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

        # [0]=Fecha,[1]=Tipo,[2]=pto_vta,[3]=Nro,[4]=Nombre,[5]=Cuit,[6]=id_paciente,[7]=Importe
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
                paciente = pacienteRepo.get_by_id(id=data[6])
                importe = float(data[7])
                facturaRepo.create(
                    tipo=data[1],
                    pto_vta=data[2],
                    numero=data[3],
                    fecha=data[0],
                    importe=importe,
                    id_beneficiario=beneficiarioExist,
                    id_paciente=paciente,
                )
            else:
                pass

        return redirect('list')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class FacturasList(View):
    context_object_name = 'facturas'

    def get(self, request):
        pago_filter = request.GET.get('pago')
        
        filterset = FacturasFilter(request.GET, queryset=facturaRepo.get_all())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', '-fecha')
        # Obtener el queryset filtrado
        facturas = filterset.qs
        # Aplicar el ordenamiento si existe
        if ordering:
            facturas = facturas.order_by(ordering)

        for factura in facturas:
            factura_paga_exists = detalleOrdenRepo.filter_by_factura_exists(id_factura=factura.id)
            factura.pago = factura_paga_exists
            factura.pto_vta = factura.pto_vta.zfill(4)
            factura.numero = factura.numero.zfill(8)

        filtros_pago = {
            'true': lambda f: f.pago is True,
            'false': lambda f: f.pago is False,
        }

        if pago_filter in filtros_pago:
            facturas = list(filter(filtros_pago[pago_filter], facturas))

        facturas_count = len(facturas)

        total = 0
        for factura in facturas:
            total += factura.importe
            factura.importe = locale.currency(factura.importe, grouping=True)

        total = locale.currency(total, grouping=True)

        return render(
            request,
            'libro_ventas/list.html',
            dict(
                facturas=facturas,
                facturas_count=facturas_count,
                form=filterset.form,
                ordering=ordering,
                total=total,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class FacturasToCsv(View):
    def get(self, request):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=facturas.xlsx'

        beneficiario_nombre = request.GET.get('id_beneficiario__nombre')
        numero_cuit = request.GET.get('id_beneficiario__numero_cuit')
        fecha_after = request.GET.get('fecha_after')
        fecha_before = request.GET.get('fecha_before')
        pago = request.GET.get('pago')

        facturas = facturaRepo.get_all()

        if beneficiario_nombre:
            facturas = facturas.filter(id_beneficiario__nombre__icontains=beneficiario_nombre)

        if numero_cuit:
            facturas = facturas.filter(id_beneficiario__numero_cuit__icontains=numero_cuit)

        if fecha_after and fecha_before:
            facturas = facturas.filter(fecha__gte=fecha_after, fecha__lt=fecha_before)

        for factura in facturas:
            factura_paga_exists = detalleOrdenRepo.filter_by_factura_exists(id_factura=factura.id)
            factura.pago = factura_paga_exists
            factura.pto_vta = factura.pto_vta.zfill(4)
            factura.numero = factura.numero.zfill(8)

        filtros_pago = {
            'true': lambda f: f.pago is True,
            'false': lambda f: f.pago is False,
        }

        if pago in filtros_pago:
            facturas = list(filter(filtros_pago[pago], facturas))

        data = []
        for factura in facturas:
            data.append([
                factura.id_beneficiario.nombre,
                factura.id_beneficiario.numero_cuit,
                factura.fecha,
                factura.pto_vta,
                factura.numero,
                factura.importe,
                factura.pago,
                ])

        df = pandas.DataFrame(data, columns=[
            'Beneficiario',
            'Nro Cuit',
            'Fecha',
            'Pto Venta',
            'Numero',
            'Importe',
            'Pagada',
            ])

        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Facturas', index=False)

        response.write(output.getvalue())

        return response


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class BalanceList(View):
    context_object_name = 'BalanceList'

    def get(self, request, id):
        beneficiario = beneficiarioRepo.filter_by_id(id=id)
        filterset = FacturasFilter(request.GET, queryset=facturaRepo.filter_by_beneficiario_id(id_beneficiario=id))

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')
        # Obtener el queryset filtrado
        facturas = filterset.qs
        # Aplicar el ordenamiento si existe
        if ordering:
            facturas = facturas.order_by(ordering)

        facturas_count = facturas.count()

        total = 0
        total_saldado = 0
        total_deuda = 0
        for factura in facturas:
            total += factura.importe
            factura.pto_vta = factura.pto_vta.zfill(4)
            factura.numero = factura.numero.zfill(8)
            factura_in_orden = detalleOrdenRepo.filter_by_factura_id(factura_id=factura.id)
            if factura_in_orden:
                factura.paga = True
                total_saldado = total_saldado + factura.importe
            else:
                factura.paga = False
                total_deuda = total_deuda + factura.importe
            factura.importe = locale.currency(factura.importe, grouping=True)

        total_descuentos = 0
        ordenes_pago = ordenPagoRepo.filter_by_beneficiario(id_beneficiario=beneficiario.id)
        for orden in ordenes_pago:
            descuentos = descuentoRepo.filter_by_orden_id(orden_id=orden.id)
            for descuento in descuentos:
                total_descuentos = total_descuentos + descuento.importe

        total_menos_dtos = total - total_descuentos

        total = locale.currency(total, grouping=True)
        total_saldado = locale.currency(total_saldado, grouping=True)
        total_deuda = locale.currency(total_deuda, grouping=True)
        total_descuentos = locale.currency(total_descuentos, grouping=True)
        total_menos_dtos = locale.currency(total_menos_dtos, grouping=True)

        return render(
            request,
            'libro_ventas/balance_list.html',
            dict(
                beneficiario=beneficiario,
                facturas=facturas,
                facturas_count=facturas_count,
                form=filterset.form,
                ordering=ordering,
                total=total,
                total_saldado=total_saldado,
                total_deuda=total_deuda,
                total_descuentos=total_descuentos,
                total_menos_dtos=total_menos_dtos,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Finanzas"), name="dispatch")
class BalanceListAll(View):
    context_object_name = 'BalanceListAll'

    def get(self, request):
        filterset = FacturasFilter(request.GET, queryset=facturaRepo.get_all())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')
        # Obtener el queryset filtrado
        facturas = filterset.qs
        # Aplicar el ordenamiento si existe
        if ordering:
            facturas = facturas.order_by(ordering)

        facturas_count = facturas.count()

        total = 0
        total_saldado = 0
        total_deuda = 0
        for factura in facturas:
            total += factura.importe
            factura.pto_vta = factura.pto_vta.zfill(4)
            factura.numero = factura.numero.zfill(8)
            factura_in_orden = detalleOrdenRepo.filter_by_factura_id(factura_id=factura.id)
            if factura_in_orden:
                factura.paga = True
                total_saldado = total_saldado + factura.importe
            else:
                factura.paga = False
                total_deuda = total_deuda + factura.importe
            factura.importe = locale.currency(factura.importe, grouping=True)

        beneficiarios = beneficiarioRepo.get_all()
        total_descuentos = 0
        for beneficiario in beneficiarios:
            ordenes_pago = ordenPagoRepo.filter_by_beneficiario(id_beneficiario=beneficiario.id)
            for orden in ordenes_pago:
                descuentos = descuentoRepo.filter_by_orden_id(orden_id=orden.id)
                for descuento in descuentos:
                    total_descuentos = total_descuentos + descuento.importe

        total_menos_dtos = total - total_descuentos

        total = locale.currency(total, grouping=True)
        total_saldado = locale.currency(total_saldado, grouping=True)
        total_deuda = locale.currency(total_deuda, grouping=True)
        total_descuentos = locale.currency(total_descuentos, grouping=True)
        total_menos_dtos = locale.currency(total_menos_dtos, grouping=True)

        return render(
            request,
            'libro_ventas/balance_list_all.html',
            dict(
                facturas=facturas,
                facturas_count=facturas_count,
                form=filterset.form,
                ordering=ordering,
                total=total,
                total_saldado=total_saldado,
                total_deuda=total_deuda,
                total_descuentos=total_descuentos,
                total_menos_dtos=total_menos_dtos,
            )
        )