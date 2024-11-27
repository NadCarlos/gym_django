import pandas as pd
import io

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse

from administracion.filters import AsistenciasFilter

from entrada.repositories.asistencia import AsistenciaRepository

from administracion.models import Asistencia


asistenciaRepo = AsistenciaRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AsistenciasList(View):
    template_name = 'asistencias/list.html'
    context_object_name = 'asistencias'

    def get(self, request):
        # Instanciar el filtro con los datos enviados por el formulario
        filterset = AsistenciasFilter(request.GET, queryset=asistenciaRepo.get_all())

        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'fecha')

        # Obtener el queryset filtrado
        asistencias = filterset.qs

        # Aplicar el ordenamiento si existe
        if ordering:
            asistencias = asistencias.order_by(ordering)

        return render(
            request,
            self.template_name,
            dict(
                asistencias=asistencias,
                form=filterset.form,
                ordering=ordering,
            )
        )


class AsistenciasToCsv(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=asistencias.xlsx'

        apellido = request.GET.get('apellido')
        fecha_after = request.GET.get('fecha_after')
        fecha_before = request.GET.get('fecha_before')
        id_obra_social = request.GET.get('id_prestacion_paciente__id_obra_social')
        id_prestacion = request.GET.get('id_prestacion_paciente__id_prestacion')

        asistencias = Asistencia.objects.all()

        if apellido:
            asistencias = asistencias.filter(id_prestacion_paciente__id_paciente__apellido__icontains=apellido)

        if fecha_after and fecha_before:
            asistencias = asistencias.filter(fecha__gte=fecha_after, fecha__lte=fecha_before)

        if id_obra_social:
            asistencias = asistencias.filter(id_prestacion_paciente__id_obra_social=id_obra_social)

        if id_prestacion:
            asistencias = asistencias.filter(id_prestacion_paciente__id_prestacion=id_prestacion)

        data = []
        for asistencia in asistencias:
            hora_asistencia = str(asistencia.hora).split(".")[0]
            hora_agenda = str(asistencia.id_agenda.hora_inicio).split(".")[0]
            tiempo = asistencia.id_agenda.tiempo
            profesional = asistencia.id_agenda.id_profesional_tratamiento.id_profesional.apellido
            tratamiento = asistencia.id_agenda.id_profesional_tratamiento.id_tratamiento.nombre
            if asistencia.id_agenda.id == 1 or None:
                hora_asistencia = ""
                tiempo = ""
                profesional = ""
                tratamiento = ""
            

            data.append([
                asistencia.id_prestacion_paciente.id_paciente.apellido,
                asistencia.id_prestacion_paciente.id_paciente.nombre,
                asistencia.fecha,
                hora_asistencia,
                hora_agenda,
                tiempo,
                asistencia.id_prestacion_paciente.id_obra_social.nombre,
                asistencia.id_prestacion_paciente.id_prestacion.nombre,
                profesional,
                tratamiento
            ])

        # Convert data to a DataFrame
        df = pd.DataFrame(data, columns=[
            'Apellido', 'Nombre', 'Fecha', 'Hora Registro', 'Hora Agenda', 'Tiempo Trabajado', 'Obra Social', 'Prestacion', 'Profesional', 'Tratamiento'
        ])

        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Asistencias', index=False)

        response.write(output.getvalue())

        return response