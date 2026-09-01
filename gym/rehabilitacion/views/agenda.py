import datetime
from datetime import time, date
from decimal import Decimal
from io import BytesIO

from django.contrib.staticfiles import finders
from django.db.models import Exists, OuterRef
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.decorators import requiere_areas

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


from administracion.repositories.paciente import PacienteRepository
from administracion.repositories.profesional import ProfesionalRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository
from rehabilitacion.repositories.asistencia import AsistenciaRehabRepository
from rehabilitacion.repositories.asistencia_teorica import AsistenciaRehabTeoricaRepository
from administracion.repositories.prestacion_paciente import PrestacionPacienteRepository
from administracion.repositories.tratamiento import TratamientoRepository
from administracion.repositories.profesional_area import ProfesionalAreaRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from rehabilitacion.repositories.rehabilitacion import PacienteRehabilitacionRepository

from rehabilitacion.forms import AgendaRehabCreateForm, AgendaRehabUpdateForm


pacienteRepo = PacienteRepository()
profesionalRepo = ProfesionalRepository()
agendaRehabRepo = AgendaRehabRepository()
asistenciaRehabRepo = AsistenciaRehabRepository()
asistenciaTeoricaRepo = AsistenciaRehabTeoricaRepository()
prestacionPacienteRepo = PrestacionPacienteRepository()
tratamientoRepo = TratamientoRepository()
profesionalAreaRepo = ProfesionalAreaRepository()
pacienteAreaRepo = PacienteAreaRepository()
pacienteRehabRepo = PacienteRehabilitacionRepository()
REHABILITACION_AREA_ID = 2


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaRehabList(View):
    paginate_by = 100

    def get(self, request):
        fecha_desde = parse_date(request.GET.get("fecha_desde", ""))
        fecha_hasta = parse_date(request.GET.get("fecha_hasta", ""))
        agenda_queryset = agendaRehabRepo.list_for_time_check(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
        paginator = Paginator(agenda_queryset, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get("page"))
        query_params = request.GET.copy()
        query_params.pop("page", None)

        for turno in page_obj:
            turno.duracion_calculada = self.get_duracion_calculada(turno)
            turno.tiempo_incorrecto = turno.duracion_calculada != self.normalize_tiempo(turno.tiempo)

        return render(
            request,
            'agenda/agenda_rehab_list.html',
            dict(
                agenda=page_obj,
                page_obj=page_obj,
                total_agendas=paginator.count,
                fecha_desde=request.GET.get("fecha_desde", ""),
                fecha_hasta=request.GET.get("fecha_hasta", ""),
                query_params=query_params.urlencode(),
            )
        )

    def get_duracion_calculada(self, turno):
        hora_inicio = turno.hora_inicio
        hora_fin = turno.hora_fin
        if not hora_inicio or not hora_fin:
            return Decimal("0.00")
        inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
        fin_minutos = hora_fin.hour * 60 + hora_fin.minute
        if fin_minutos <= inicio_minutos:
            return Decimal("0.00")
        duracion = Decimal(fin_minutos - inicio_minutos) / Decimal("60")
        return duracion.quantize(Decimal("0.01"))

    def normalize_tiempo(self, tiempo):
        if tiempo is None:
            return Decimal("0.00")
        return Decimal(tiempo).quantize(Decimal("0.01"))


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaPacienteRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)
        agenda = agendaRehabRepo.filter_by_paciente_area(id_paciente_area=pacienteArea.id)
        return render(
            request,
            'agenda/agenda_paciente_rehab.html',
            dict(
                path=path,
                paciente=paciente,
                agenda=agenda,
            )
        )
    

class AgendaRehabPDFMixin:

    def render_agenda_pdf(self, agenda, title, main_column_title, main_value_getter, filename):
        download_date = self.format_date(datetime.datetime.now())
        icon_path = finders.find("public/logoiteclabs.png")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=0.7 * cm,
            leftMargin=0.7 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.7 * cm,
        )

        styles = self.get_styles()
        title_style = styles["title"]
        day_style = styles["day"]
        cell_style = styles["cell"]
        cell_obs_style = styles["obs"]
        shift_style = styles["shift"]
        page_width = landscape(A4)[0] - doc.leftMargin - doc.rightMargin

        elements = [
            self.build_header(title, title_style, page_width),
            Spacer(1, 0.15 * cm),
        ]
        elements.append(
            self.build_agenda_table(
                agenda=agenda,
                main_column_title=main_column_title,
                main_value_getter=main_value_getter,
                page_width=page_width,
                day_style=day_style,
                cell_style=cell_style,
                cell_obs_style=cell_obs_style,
                shift_style=shift_style,
            )
        )

        doc.build(
            elements,
            onFirstPage=lambda canvas, doc: self.draw_footer(canvas, doc, download_date, icon_path),
            onLaterPages=lambda canvas, doc: self.draw_footer(canvas, doc, download_date, icon_path),
        )
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    def get_styles(self):
        sample_styles = getSampleStyleSheet()
        cell_style = ParagraphStyle(
            "AgendaCell",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=6.5,
            leading=8,
        )
        return {
            "title": ParagraphStyle(
                "AgendaTitle",
                parent=sample_styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=20,
                alignment=TA_CENTER,
                spaceAfter=2,
            ),
            "day": ParagraphStyle(
                "DayTitle",
                parent=sample_styles["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#212529"),
                spaceAfter=4,
            ),
            "cell": cell_style,
            "obs": ParagraphStyle(
                "AgendaObsCell",
                parent=sample_styles["BodyText"],
                fontName="Helvetica",
                fontSize=5,
                leading=8,
            ),
            "shift": ParagraphStyle(
                "AgendaShift",
                parent=cell_style,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#212529"),
            ),
        }

    def build_header(self, title, title_style, page_width):
        logo_path = finders.find("public/cermed_sin_fondo.png")
        header_logo = ""
        if logo_path:
            header_logo = Image(logo_path, width=2 * cm, height=2 * cm)

        header_table = Table(
            [[header_logo, Paragraph(title, title_style), ""]],
            colWidths=[2.3 * cm, page_width - 4.6 * cm, 2.3 * cm],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d4faf7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return header_table

    def build_agenda_table(
        self,
        agenda,
        main_column_title,
        main_value_getter,
        page_width,
        day_style,
        cell_style,
        cell_obs_style,
        shift_style,
    ):
        days = [
            ("Lunes", "Lunes"),
            ("Martes", "Martes"),
            ("Miercoles", "Miercoles"),
            ("Jueves", "Jueves"),
            ("Viernes", "Viernes"),
        ]
        agenda_by_day = {day_name: {"morning": [], "afternoon": []} for _, day_name in days}
        afternoon_start = time(14, 0)
        for item in agenda:
            if item.id_dia and item.id_dia.nombre in agenda_by_day:
                shift = "morning" if item.hora_inicio < afternoon_start else "afternoon"
                agenda_by_day[item.id_dia.nombre][shift].append(item)

        section_rows = max(
            [
                len(day_agenda[shift])
                for day_agenda in agenda_by_day.values()
                for shift in ("morning", "afternoon")
            ] + [5]
        )

        day_width = page_width / 5
        day_tables = []
        for day_label, day_name in days:
            rows = [[
                Paragraph("Inicio", cell_style),
                Paragraph("Fin", cell_style),
                Paragraph(main_column_title, cell_style),
                Paragraph("Obs.", cell_obs_style),
            ]]

            shift_rows = [
                self.add_shift_rows(
                    rows,
                    "Mañana",
                    agenda_by_day[day_name]["morning"],
                    section_rows,
                    main_value_getter,
                    cell_style,
                    cell_obs_style,
                    shift_style,
                ),
                self.add_shift_rows(
                    rows,
                    "Tarde",
                    agenda_by_day[day_name]["afternoon"],
                    section_rows,
                    main_value_getter,
                    cell_style,
                    cell_obs_style,
                    shift_style,
                ),
            ]
            row_heights = [
                0.42 * cm if index == 0 or index in shift_rows else 0.58 * cm
                for index in range(len(rows))
            ]

            schedule_table = Table(
                rows,
                colWidths=[1.0 * cm, 1.0 * cm, day_width - 3.3 * cm, 0.8 * cm],
                rowHeights=row_heights,
                repeatRows=1,
            )
            schedule_style = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#53c0b8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#212529")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.5),
                ("ALIGN", (0, 0), (1, -1), "CENTER"),
                ("ALIGN", (3, 0), (3, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#adb5bd")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]
            for shift_row in shift_rows:
                schedule_style.extend([
                    ("SPAN", (0, shift_row), (-1, shift_row)),
                    ("BACKGROUND", (0, shift_row), (-1, shift_row), colors.HexColor("#e9ecef")),
                ])
            schedule_table.setStyle(TableStyle(schedule_style))

            day_table = Table(
                [[Paragraph(day_label, day_style)], [schedule_table]],
                colWidths=[day_width - 0.12 * cm],
            )
            day_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#d4faf7")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]))
            day_tables.append(day_table)

        agenda_table = Table([day_tables], colWidths=[day_width] * 5)
        agenda_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        return agenda_table

    def add_shift_rows(
        self,
        rows,
        title,
        items,
        max_rows,
        main_value_getter,
        cell_style,
        cell_obs_style,
        shift_style,
    ):
        shift_row = len(rows)
        rows.append([Paragraph(title, shift_style), "", "", ""])
        for item in items:
            rows.append([
                self.format_time(item.hora_inicio),
                self.format_time(item.hora_fin),
                Paragraph(str(main_value_getter(item)), cell_style),
                Paragraph(item.observaciones or "", cell_obs_style),
            ])
        for _ in range(max_rows - len(items)):
            rows.append(["", "", "", ""])
        return shift_row

    def format_time(self, value):
        if not value:
            return ""
        return value.strftime("%H:%M")

    def format_date(self, value):
        meses = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }
        return f"{value.day} de {meses[value.month]} de {value.year}"

    def draw_footer(self, canvas, doc, download_date, icon_path):
        footer_y = 0.6 * cm
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.HexColor("#6c757d"))
        if icon_path:
            icon_size = 1.5 * cm
            canvas.drawImage(
                icon_path,
                doc.leftMargin,
                footer_y - 0.20 * cm,
                width=icon_size,
                height=icon_size,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawString(doc.leftMargin + 0.45 * cm, footer_y, "           Sistema ASISPRO powered by ITEClabs")
        else:
            canvas.drawString(doc.leftMargin, footer_y, "           Sistema ASISPRO powered by ITEClabs")
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            footer_y,
            f"Rio Cuarto el {download_date}",
        )
        canvas.restoreState()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaPacienteRehabToPDF(AgendaRehabPDFMixin, View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)
        agenda = agendaRehabRepo.filter_by_paciente_area(id_paciente_area=pacienteArea.id)
        filename = f"agenda_{paciente.apellido}_{paciente.nombre}.pdf".replace(" ", "_")
        return self.render_agenda_pdf(
            agenda=agenda,
            title=f"Agenda Paciente: {paciente.apellido}, {paciente.nombre}",
            main_column_title="Prestacion",
            main_value_getter=lambda item: item.id_tratamiento_rehab.nombre,
            filename=filename,
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaPacienteRehabCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        date = datetime.datetime.now()
        dateSTR = date.strftime("%d-%m-%Y")
        tratamientosActivos = tratamientoRepo.filter_by_activo()
        form = AgendaRehabCreateForm(
            initial = {
                'id_usuario': request.user,
                'fecha': date,
            }
        )
        return render(
            request,
            'agenda/rehab_create.html',
            dict(
                paciente=paciente,
                tratamientosActivos=tratamientosActivos,
                dateSTR=dateSTR,
                form=form,
            )
        )
    
    def post(self, request, id):
        form = AgendaRehabCreateForm(request.POST)
        error_message = None
        if form.is_valid():
            paciente = pacienteRepo.get_by_id(id=id)
            pacienteArea = pacienteAreaRepo.filter_by_id_area_and_paciente(id_area=2, id_paciente=paciente.id)

            tratamiento_id = request.POST.get('id_tratamiento')
            tratamiento = tratamientoRepo.get_by_id(id=tratamiento_id)

            profesional_id = request.POST.get('profesional')
            profesional = profesionalRepo.filter_by_id(id=profesional_id)
            profesionalArea = None
            if profesional is not None:
                profesionalArea = profesionalAreaRepo.filter_by_profesional_id(
                    id_profesional=profesional.id,
                    id_area=2,
                )

            if tratamiento is None or profesional is None or profesionalArea is None or pacienteArea is None:
                error_message = 'Debe seleccionar un tratamiento y un profesional de Rehabilitación.'
            else:
                hora_inicio = form.cleaned_data['hora_inicio']
                hora_fin = form.cleaned_data['hora_fin']
                # Convierte horas y minutos a minutos totales para ambos tiempos
                hora_inicio_total_minutos = hora_inicio.hour * 60 + hora_inicio.minute
                hora_fin_total_minutos = hora_fin.hour * 60 + hora_fin.minute
                if hora_fin_total_minutos <= hora_inicio_total_minutos:
                    return redirect('error_hora')
                diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
                diferencia_horas = diferencia_minutos / 60

                observaciones = form.cleaned_data['observaciones']
                if observaciones:
                    observaciones = observaciones.upper()

                paciente_rehab = pacienteRehabRepo.get_by_paciente_id_item(id_paciente=paciente.id)
                if paciente_rehab is not None and paciente_rehab.pre_ingreso == 1:
                    observaciones = "R"
                
                agendaRehabRepo.create(
                    id_usuario=form.cleaned_data['id_usuario'],
                    fecha=form.cleaned_data['fecha'],
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    id_dia=form.cleaned_data['id_dia'],
                    tiempo=diferencia_horas,
                    id_tratamiento_rehab=tratamiento,
                    id_paciente_area=pacienteArea,
                    id_profesional_area=profesionalArea,
                    observaciones=observaciones,
                )

                return redirect('agenda_paciente_rehab', paciente.id)

        paciente = pacienteRepo.get_by_id(id=id)
        return render(
            request,
            'agenda/rehab_create.html',
            dict(
                paciente=paciente,
                tratamientosActivos=tratamientoRepo.filter_by_activo(),
                dateSTR=datetime.datetime.now().strftime("%d-%m-%Y"),
                form=form,
                error_message=error_message,
            ),
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaPacienteRehabDetail(View):

    def get(self, request, id):
        agenda = agendaRehabRepo.get_by_id(id=id)
        paciente = agenda.id_paciente_area.id_paciente
        profesional_old = agenda.id_profesional_area.id_profesional
        tratamiento_old = agenda.id_tratamiento_rehab
        return render(
            request,
            'agenda/rehab_detail.html',
            dict(
                agenda=agenda,
                paciente=paciente,
                profesional_old=profesional_old,
                tratamiento_old=tratamiento_old,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaPacienteRehabUpdate(View):

    def get(self, request, id):
        agenda = agendaRehabRepo.get_by_id(id=id)
        paciente = agenda.id_paciente_area.id_paciente
        profesional_old = agenda.id_profesional_area.id_profesional
        tratamiento_old = agenda.id_tratamiento_rehab
        tratamientosActivos = tratamientoRepo.filter_by_activo()
        form = AgendaRehabUpdateForm(instance=agenda)
        return render(
            request,
            'agenda/rehab_update.html',
            dict(
                form=form,
                paciente=paciente,
                tratamientosActivos=tratamientosActivos,
                profesional_old=profesional_old,
                tratamiento_old=tratamiento_old,
            )
        )
    
    def post(self, request, id):
        agenda = agendaRehabRepo.get_by_id(id=id)
        form = AgendaRehabUpdateForm(request.POST)
        path = request.session.get('uid')
        error_message = None
        if form.is_valid():
            tratamiento_id = request.POST.get('id_tratamiento')
            tratamiento = tratamientoRepo.filter_by_id(id=tratamiento_id)

            profesional_id = request.POST.get('profesional')
            profesional = profesionalRepo.filter_by_id(id=profesional_id)
            profesionalArea = None
            if profesional is not None:
                profesionalArea = profesionalAreaRepo.filter_by_profesional_id(
                    id_profesional=profesional.id,
                    id_area=2,
                )

            if tratamiento is None or profesional is None or profesionalArea is None:
                error_message = 'Debe seleccionar un tratamiento y un profesional de Rehabilitación.'
            else:
                hora_inicio = form.cleaned_data['hora_inicio']
                hora_fin = form.cleaned_data['hora_fin']
                # Convierte horas y minutos a minutos totales para ambos tiempos
                hora_inicio_total_minutos = hora_inicio.hour * 60 + hora_inicio.minute
                hora_fin_total_minutos = hora_fin.hour * 60 + hora_fin.minute
                if hora_fin_total_minutos <= hora_inicio_total_minutos:
                    return redirect('error_hora')
                diferencia_minutos = hora_fin_total_minutos - hora_inicio_total_minutos
                diferencia_horas = diferencia_minutos / 60

                observaciones = form.cleaned_data['observaciones']
                if observaciones:
                    observaciones = observaciones.upper()

                agendaRehabRepo.update(
                    agenda=agenda,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    id_dia=form.cleaned_data['id_dia'],
                    tiempo=diferencia_horas,
                    id_tratamiento_rehab=tratamiento,
                    id_profesional_area=profesionalArea,
                    observaciones=observaciones,
                )

                if path:
                    return redirect(path)
                return redirect("agenda_paciente_rehab", agenda.id_paciente_area.id_paciente_id)

        return render(
            request,
            'agenda/rehab_update.html',
            dict(
                form=form,
                paciente=agenda.id_paciente_area.id_paciente,
                tratamientosActivos=tratamientoRepo.filter_by_activo(),
                profesional_old=agenda.id_profesional_area.id_profesional,
                tratamiento_old=agenda.id_tratamiento_rehab,
                error_message=error_message,
            ),
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class AgendaRehabDelete(View):
    http_method_names = ["post"]

    def post(self, request, id, *args, **kwargs):
        path = request.session.get('uid')
        agenda = agendaRehabRepo.get_by_id(id=id)
        today = date.today()
        agendaRehabRepo.deactivate(agenda=agenda, fecha_fin=today)
        return redirect( path )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaProfesionalRehab(View):

    def get(self, request, id):
        path = request.session['uid'] = request.path
        profesional = profesionalRepo.get_by_id(id=id)
        if not profesional:
            return redirect('error')
        profesionalArea = profesionalAreaRepo.filter_by_profesional_id(
            id_profesional=profesional.id,
            id_area=REHABILITACION_AREA_ID,
        )
        if not profesionalArea:
            return redirect('error')
        today = date.today()
        primer_dia_mes = today.replace(day=1)
        if today.month == 12:
            primer_dia_mes_siguiente = date(today.year + 1, 1, 1)
        else:
            primer_dia_mes_siguiente = date(today.year, today.month + 1, 1)

        horas_teoricas_mes = asistenciaTeoricaRepo.total_horas_por_profesional_area(
            id_profesional_area=profesionalArea.id,
            fecha_desde=primer_dia_mes,
            fecha_hasta=primer_dia_mes_siguiente,
            id_area=REHABILITACION_AREA_ID,
        )
        asistencia_cargada = asistenciaRehabRepo.filter_by_agenda_date(
            id_agenda_rehab=OuterRef("pk"),
            fecha=today,
        )
        agenda = agendaRehabRepo.filter_by_id_profesional_area(
            id_profesional_area=profesionalArea.id,
        ).annotate(
            asistencia_cargada=Exists(asistencia_cargada),
        )
        dias = [
            (1, "Lunes"),
            (2, "Martes"),
            (3, "Miércoles"),
            (4, "Jueves"),
            (5, "Viernes"),
        ]
        return render(
            request,
            'agenda/agenda_profesional_rehab.html',
            dict(
                path=path,
                profesional=profesional,
                agenda=agenda,
                horas_teoricas_mes=horas_teoricas_mes,
                mes_actual=today.strftime("%m/%Y"),
                dia_actual=today.weekday() + 1,
                hora_limite_tarde=time(14, 0),
                dias=dias,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class AgendaProfesionalRehabToPDF(AgendaRehabPDFMixin, View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        if not profesional:
            return redirect('error')
        profesionalArea = profesionalAreaRepo.filter_by_profesional_id(
            id_profesional=profesional.id,
            id_area=REHABILITACION_AREA_ID,
        )
        if not profesionalArea:
            return redirect('error')
        agenda = agendaRehabRepo.filter_by_id_profesional_area(id_profesional_area=profesionalArea.id)
        filename = f"agenda_profesional_{profesional.apellido}_{profesional.nombre}.pdf".replace(" ", "_")
        return self.render_agenda_pdf(
            agenda=agenda,
            title=f"Agenda Profesional: {profesional.apellido}, {profesional.nombre}",
            main_column_title="Paciente",
            main_value_getter=lambda item: item.id_paciente_area.id_paciente.apellido,
            filename=filename,
        )
