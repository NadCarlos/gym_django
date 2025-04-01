import pandas as pd
import io
import datetime
from datetime import time, date

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.agenda import AgendaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository

from administracion.forms import AgendaCreateForm, AgendaUpdateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRepo = AgendaRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPaciente(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        agenda = agendaRepo.filter_by_id_paciente(id_prestacion_paciente=prestacion.id)
        return render(
            request,
            'agenda/agenda_paciente.html',
            dict(
                path=path,
                paciente=paciente,
                agenda=agenda,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPacienteCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        if prestacion is None:
            return redirect('error_prestacion_paciente')
        date = datetime.datetime.now()
        dateSTR = date.strftime("%d-%m-%Y")
        profesionales = profesionalRepo.filter_by_activo()
        tratamientosActivos = tratamientoProfesionalRepo.filter_by_activo()
        form = AgendaCreateForm(
            initial = {
                'id_usuario': request.user,
                'fecha': date,
            }
        )
        return render(
            request,
            'agenda/create.html',
            dict(
                paciente=paciente,
                profesionales=profesionales,
                tratamientosActivos=tratamientosActivos,
                dateSTR=dateSTR,
                form=form,
            )
        )
    
    def post(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        prestacion = prestacionPacienteRepo.filter_by_id_paciente_activo(id_paciente=paciente.id)
        form = AgendaCreateForm(request.POST)
        if form.is_valid():
            hora_inicio=form.cleaned_data['hora_inicio'],
            hora_fin=form.cleaned_data['hora_fin'],

            # Convierte horas y minutos a minutos totales para ambos tiempos
            hora_inicio_total_minutos = hora_inicio[0].hour * 60 + hora_inicio[0].minute
            hora_fin_total_minutos = hora_fin[0].hour * 60 + hora_fin[0].minute
            if hora_fin_total_minutos <= hora_inicio_total_minutos:
                return redirect('error_hora')
            diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
            diferencia_horas = diferencia_minutos / 60
            
            agendaRepo.create(
                id_usuario=form.cleaned_data['id_usuario'],
                fecha=form.cleaned_data['fecha'],
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                id_prestacion_paciente=prestacion,
                id_profesional_tratamiento=form.cleaned_data['id_profesional_tratamiento'],
                id_dia=form.cleaned_data['id_dia'],
                tiempo=diferencia_horas,
            )

            return redirect('agenda_paciente', paciente.id)
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaPacienteUpdate(View):

    def get(self, request, id):
        agenda = agendaRepo.get_by_id(id=id)
        paciente = agenda.id_prestacion_paciente.id_paciente
        profesionales = profesionalRepo.filter_by_activo()
        profesional_old = agenda.id_profesional_tratamiento.id_profesional
        tratamiento_old = agenda.id_profesional_tratamiento
        tratamientosActivos = tratamientoProfesionalRepo.filter_by_activo()
        form = AgendaUpdateForm(instance=agenda)
        return render(
            request,
            'agenda/update.html',
            dict(
                form=form,
                profesionales=profesionales,
                paciente=paciente,
                tratamientosActivos=tratamientosActivos,
                profesional_old=profesional_old,
                tratamiento_old=tratamiento_old,
            )
        )
    
    def post(self, request, id):
        agenda = agendaRepo.get_by_id(id=id)
        form = AgendaUpdateForm(request.POST)
        path = request.session.get('uid')
        if form.is_valid():
            hora_inicio=form.cleaned_data['hora_inicio'],
            hora_fin=form.cleaned_data['hora_fin'],

            # Convierte horas y minutos a minutos totales para ambos tiempos
            hora_inicio_total_minutos = hora_inicio[0].hour * 60 + hora_inicio[0].minute
            hora_fin_total_minutos = hora_fin[0].hour * 60 + hora_fin[0].minute
            if hora_fin_total_minutos <= hora_inicio_total_minutos:
                return redirect('error_hora')
            diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
            diferencia_horas = diferencia_minutos / 60
            
            agendaRepo.update(
                agenda=agenda,
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                id_profesional_tratamiento=form.cleaned_data['id_profesional_tratamiento'],
                id_dia=form.cleaned_data['id_dia'],
                tiempo=diferencia_horas,
            )

            return redirect( path )
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaDelete(View):

    def get(self, request, id, *args, **kwargs):
        path = request.session.get('uid')
        agenda = agendaRepo.get_by_id(id=id)
        today = date.today()
        agendaRepo.end_date(
            agenda=agenda,
            fecha_fin=today,
            )
        #No elimino, cambio el campo activo a False
        agendaRepo.delete_by_activo(agenda=agenda)
        return redirect( path )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaProfesional(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        profesional = profesionalRepo.get_by_id(id=id)
        agenda = agendaRepo.filter_by_activo(state=True)
        return render(
            request,
            'agenda/agenda_profesional.html',
            dict(
                path=path,
                profesional=profesional,
                agenda=agenda,
                hora_limite_tarde=time(14, 0),
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaProfesionalToCsv(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        nombre_profesional = profesional.nombre
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=agenda_profesional_{nombre_profesional}.xlsx'
        agenda = agendaRepo.filter_by_activo_profesional(state=True, id_profesional=id)

        data = []
        data_lunes = []
        data_martes = []
        data_miercoles = []
        data_jueves = []
        data_viernes = []
        for entrada in agenda:
            hora_inicio = str(entrada.hora_inicio).split(".")[0]
            hora_fin = str(entrada.hora_fin).split(".")[0]
            nombre_completo = entrada.id_prestacion_paciente.id_paciente.apellido + ", " + entrada.id_prestacion_paciente.id_paciente.nombre
            if entrada.id_dia.id == 1:
                data_lunes.append([
                    nombre_completo,
                    hora_inicio,
                    hora_fin,
                ])
            if entrada.id_dia.id == 2:
                data_martes.append([
                    nombre_completo,
                    hora_inicio,
                    hora_fin,
                ])
            if entrada.id_dia.id == 3:
                data_miercoles.append([
                    nombre_completo,
                    hora_inicio,
                    hora_fin,
                ])
            if entrada.id_dia.id == 4:
                data_jueves.append([
                    nombre_completo,
                    hora_inicio,
                    hora_fin,
                ])
            if entrada.id_dia.id == 5:
                data_viernes.append([
                    nombre_completo,
                    hora_inicio,
                    hora_fin,
                ])

        data = {
            "Lunes": data_lunes,
            "Martes": data_martes,
            "Miércoles": data_miercoles,
            "Jueves": data_jueves,
            "Viernes": data_viernes,
        }

        max_length = max(len(v) for v in data.values())

        formatted_data = {}
        for day, entries in data.items():
            nombres = [entry[0] for entry in entries]
            hora_inicio = [entry[1] for entry in entries]
            hora_fin = [entry[2] for entry in entries]
            
            # Rellenar con valores vacíos si es necesario
            nombres.extend([""] * (max_length - len(nombres)))
            hora_inicio.extend([""] * (max_length - len(hora_inicio)))
            hora_fin.extend([""] * (max_length - len(hora_fin)))

            formatted_data[f"{day}"] = nombres
            formatted_data[f"{day}_Hora I"] = hora_inicio
            formatted_data[f"{day}_Hora F"] = hora_fin

        df = pd.DataFrame(formatted_data)
        
        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='agenda_profesional', index=False)

        response.write(output.getvalue())

        return response


@method_decorator(login_required(login_url='login'), name='dispatch')
class ErrorPrestacionFaltante(View):

    def get(self, request):
        return render(
            request,
            'agenda/error_prestacion_paciente.html',
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ErrorHora(View):

    def get(self, request):
        return render(
            request,
            'agenda/error_hora.html',
        )