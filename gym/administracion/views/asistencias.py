import csv
from typing import Any
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse

from administracion.filters import AsistenciasFilter

from entrada.repositories.asistencia import AsistenciaRepository

from administracion.models import Asistencia


asisteniaRepo = AsistenciaRepository()

@method_decorator(login_required(login_url='login'), name='dispatch')
class AsistenciasList(View):
    queryset = asisteniaRepo.get_all()
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get(self, request):
        asistencias = self.queryset
        return render (
            request,
            self.template_name,
            dict(
                asistencias=asistencias,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AsistenciasList(View):
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get(self, request):
        # Instanciar el filtro con los datos enviados por el formulario
        filterset = AsistenciasFilter(request.GET, queryset=asisteniaRepo.get_all())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')  # Por defecto ordenar por fecha

        # Obtener el queryset filtrado
        asistencias = filterset.qs

        # Aplicar el ordenamiento si existe
        if ordering:
            asistencias = asistencias.order_by(ordering)

        return render(
            request,
            self.template_name,
            dict(
                asistencias=asistencias,  # Pasamos las asistencias filtradas y ordenadas
                form=filterset.form,  # Pasamos el formulario del filtro al template
                ordering=ordering,  # Pasamos el orden actual para su uso en el template
            )
        )



class AsistenciasToCsv(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=asistencias.xlsx'
        writer = csv.writer(response)

        writer.writerow([
            'Apellido',
            'Nombre',
            'Fecha',
            'Hora',
            'Obra Social',
            'Prestacion',
            ])
        
        apellido = request.GET.get('apellido')
        fecha_after = request.GET.get('fecha_after')
        fecha_before = request.GET.get('fecha_before')
        id_obra_social = request.GET.get('id_prestacion_paciente__id_obra_social')
        id_prestacion = request.GET.get('id_prestacion_paciente__id_prestacion')

        asistencias = Asistencia.objects.all()

        if apellido:
            asistencias = asistencias.filter(apellido__icontains=apellido)

        if fecha_after and fecha_before:
            asistencias = asistencias.filter(fecha__gte=fecha_after, fecha__lte=fecha_before)

        if id_obra_social:
            asistencias = asistencias.filter(id_prestacion_paciente__id_obra_social=id_obra_social)

        if id_prestacion:
            asistencias = asistencias.filter(id_prestacion_paciente__id_prestacion=id_prestacion)

        for asistencia in asistencias:
            print(asistencia.id_prestacion_paciente.id_obra_social.nombre)
            writer.writerow([
                asistencia.id_prestacion_paciente.id_paciente.apellido,
                asistencia.id_prestacion_paciente.id_paciente.nombre,
                asistencia.fecha,
                asistencia.hora,
                asistencia.id_prestacion_paciente.id_obra_social.nombre,
                asistencia.id_prestacion_paciente.id_prestacion.nombre
                ])
        return response