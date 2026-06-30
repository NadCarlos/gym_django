from io import BytesIO

from datetime import date, datetime, timedelta, time
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views import View
from django.contrib.staticfiles import finders

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepInFrame
)

from utils.decorators import requiere_areas

from rehabilitacion.forms import TurnoCreateForm, TurnoUpdateForm

from rehabilitacion.repositories.turno import TurnoRepository
from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.paciente_area import PacienteAreaRepository
from administracion.repositories.tratamiento_profesional import TratamientoProfesionalRepository


turnoRepo = TurnoRepository()
profesionalRepo = ProfesionalRepository()
pacienteAreaRepo = PacienteAreaRepository()
tratamientoProfesionalRepo = TratamientoProfesionalRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TurnoList(View):

    def get(self, request):
        profesional_id = request.GET.get('profesional')
        fecha = self.get_fecha_referencia(request.GET.get('fecha'))
        lunes = fecha - timedelta(days=fecha.weekday())
        viernes = lunes + timedelta(days=4)
        profesionales = profesionalRepo.filter_profesional_area(id_area=2)
        turnos = []
        if profesional_id:
            turnos = list(turnoRepo.filter_by_profesional_and_rango_fecha(
                profesional_id=profesional_id,
                fecha_inicio=lunes,
                fecha_fin=viernes,
            ))

        nombres_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        hora_limite_tarde = time(14, 0)

        agenda_dias = []
        for index, nombre in enumerate(nombres_dias):
            fecha_dia = lunes + timedelta(days=index)
            turnos_dia = [turno for turno in turnos if turno.fecha == fecha_dia]
            agenda_dias.append({
                "nombre": nombre,
                "fecha": fecha_dia,
                "manana": [turno for turno in turnos_dia if turno.hora < hora_limite_tarde],
                "tarde": [turno for turno in turnos_dia if turno.hora >= hora_limite_tarde],
            })

        return render(
            request,
            'turnos/list.html',
            dict(
                profesionales=profesionales,
                profesional_id=profesional_id,
                fecha=fecha.isoformat(),
                semana_inicio=lunes,
                semana_fin=viernes,
                agenda_dias=agenda_dias,
                turnos=turnos,
            )
        )
    
    def get_fecha_referencia(self, fecha):
        if not fecha:
            return date.today()
        try:
            return datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return date.today()
    

class TurnosRehabPDFMixin:
    ESTADO_LETRA = {
        "programado": "P",
        "realizado": "R",
        "anulado": "A",
    }
    ESTADO_COLOR = {
        "P": colors.HexColor("#28a745"),  # verde
        "R": colors.HexColor("#2f6fed"),  # azul
        "A": colors.HexColor("#dc3545"),  # rojo
    }

    def get_styles(self):
        sample = getSampleStyleSheet()
        return {
            "titulo": ParagraphStyle(
                "Titulo", parent=sample["Title"], fontName="Helvetica-Bold",
                fontSize=12, alignment=TA_CENTER, spaceAfter=3,
            ),
            "dia_nombre": ParagraphStyle(
                "DiaNombre", parent=sample["Heading3"], fontName="Helvetica-Bold",
                fontSize=9.5, alignment=TA_CENTER, textColor=colors.HexColor("#212529"),
                leading=11,
            ),
            "dia_fecha": ParagraphStyle(
                "DiaFecha", parent=sample["Normal"], fontName="Helvetica",
                fontSize=6.5, alignment=TA_CENTER, textColor=colors.HexColor("#495057"),
                leading=8,
            ),
            "turno_title": ParagraphStyle(
                "TurnoTitle", parent=sample["Normal"], fontName="Helvetica-Bold",
                fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor("#495057"),
            ),
            "hora": ParagraphStyle(
                "Hora", parent=sample["Normal"], fontName="Helvetica-Bold",
                fontSize=6.5, textColor=colors.HexColor("#212529"),
            ),
            "badge": ParagraphStyle(
                "Badge", parent=sample["Normal"], fontName="Helvetica-Bold",
                fontSize=6, alignment=TA_CENTER, textColor=colors.white,
            ),
            "nombre": ParagraphStyle(
                "Nombre", parent=sample["Normal"], fontName="Helvetica-Bold",
                fontSize=6.5, textColor=colors.HexColor("#212529"), leading=8,
            ),
            "subtitulo": ParagraphStyle(
                "Subtitulo", parent=sample["Normal"], fontName="Helvetica",
                fontSize=5.5, textColor=colors.HexColor("#868e96"), leading=7,
            ),
            "sin_turnos": ParagraphStyle(
                "SinTurnos", parent=sample["Normal"], fontName="Helvetica-Oblique",
                fontSize=6.5, alignment=TA_CENTER, textColor=colors.HexColor("#adb5bd"),
            ),
        }

    def render_turnos_pdf(self, agenda_dias, titulo, filename):
        download_date = self.format_date(datetime.now())
        icon_path = finders.find("public/logoiteclabs.png")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=0.6 * cm,
            leftMargin=0.6 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.7 * cm,
        )
        styles = self.get_styles()
        page_width = landscape(A4)[0] - doc.leftMargin - doc.rightMargin
        day_width = page_width / 5

        day_columns = [
            self.build_dia_column(dia, styles, day_width)
            for dia in agenda_dias
        ]

        agenda_row = Table([day_columns], colWidths=[day_width] * 5)
        agenda_row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        title_block_height = 0.9 * cm
        available_height = (
            landscape(A4)[1] - doc.topMargin - doc.bottomMargin - title_block_height
        )

        framed_agenda = KeepInFrame(
            maxWidth=page_width,
            maxHeight=available_height,
            content=[agenda_row],
            mode="shrink",
            hAlign="CENTER",
        )

        elements = [
            Paragraph(titulo, styles["titulo"]),
            framed_agenda,
        ]

        doc.build(
            elements,
            onFirstPage=lambda canvas, doc: self.draw_footer(canvas, doc, download_date, icon_path),
            onLaterPages=lambda canvas, doc: self.draw_footer(canvas, doc, download_date, icon_path),
        )
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    def build_dia_column(self, dia, styles, day_width):
        inner_width = day_width - 0.2 * cm

        rows = [
            [Paragraph(dia["nombre"], styles["dia_nombre"])],
            [Paragraph(self.format_date(dia["fecha"]), styles["dia_fecha"])],
        ]
        rows += self.build_turno_section_rows("Mañana", dia["manana"], styles, inner_width)
        rows += self.build_turno_section_rows("Tarde", dia["tarde"], styles, inner_width)

        column = Table(rows, colWidths=[inner_width])
        column.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#d7e8ff")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        return column

    def build_turno_section_rows(self, titulo, turnos, styles, inner_width):
        banner = Table([[Paragraph(titulo, styles["turno_title"])]], colWidths=[inner_width])
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f3f5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e9ecef")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        rows = [[banner]]
        if not turnos:
            rows.append([Paragraph("Sin turnos", styles["sin_turnos"])])
        else:
            for turno in turnos:
                rows.append([self.build_turno_card(turno, styles, inner_width)])
        return rows

    def build_turno_card(self, turno, styles, card_width):
        letra = self.get_estado_letra(turno.estado)
        color = self.ESTADO_COLOR.get(letra, colors.HexColor("#868e96"))

        color_hex = f"#{color.hexval()}" if hasattr(color, 'hexval') else "#868e96"

        hora_str = self.format_time(turno.hora)
        nombre = f"{(turno.paciente_id.apellido or '')}, {(turno.paciente_id.nombre or '')}"
        hora_y_nombre = f"{hora_str} - {nombre}" if hora_str else nombre

        texto_superior = f"<font color='{color_hex}'><b>[{letra}]</b></font> {hora_y_nombre}"

        obra_social = (str(turno.paciente_id.id_obra_social) if turno.paciente_id.id_obra_social else "S/OS")
        motivo = (str(turno.motivo) if turno.motivo else "")
        subtitulo_texto = f"{obra_social} - {motivo}" if motivo else obra_social

        card = Table(
            [
                [Paragraph(texto_superior, styles["nombre"])],
                [Paragraph(subtitulo_texto, styles["subtitulo"])],
            ],
            colWidths=[card_width - 0.5 * cm],
        )
        card.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return card

    def get_estado_letra(self, estado):
        if not estado:
            return "?"
        estado_str = str(estado).strip().lower()
        return self.ESTADO_LETRA.get(estado_str, str(estado)[0].upper())

    def format_time(self, value):
        if not value:
            return ""
        return value.strftime("%H:%M")

    def format_date(self, value):
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
        }
        return f"{value.day} de {meses[value.month]} de {value.year}"

    def draw_footer(self, canvas, doc, download_date, icon_path):
        footer_y = 0.5 * cm
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6c757d"))
        if icon_path:
            icon_size = 1.0 * cm
            canvas.drawImage(
                icon_path, doc.leftMargin, footer_y - 0.1 * cm,
                width=icon_size, height=icon_size, preserveAspectRatio=True, mask="auto",
            )
            canvas.drawString(doc.leftMargin + 1.2 * cm, footer_y, "Sistema ASISPRO powered by ITEClabs")
        else:
            canvas.drawString(doc.leftMargin, footer_y, "Sistema ASISPRO powered by ITEClabs")
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, footer_y, f"Rio Cuarto el {download_date}")
        canvas.restoreState()
        

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TurnosProfesionalRehabToPDF(TurnosRehabPDFMixin, View):

    def get(self, request):
        profesional_id = request.GET.get('profesional')
        fecha = self.get_fecha_referencia(request.GET.get('fecha'))

        lunes = fecha - timedelta(days=fecha.weekday())
        viernes = lunes + timedelta(days=4)

        turnos = list(turnoRepo.filter_by_profesional_and_rango_fecha(
            profesional_id=profesional_id,
            fecha_inicio=lunes,
            fecha_fin=viernes,
        ))

        nombres_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        hora_limite_tarde = time(14, 0)
        agenda_dias = []
        for index, nombre in enumerate(nombres_dias):
            fecha_dia = lunes + timedelta(days=index)
            turnos_dia = [t for t in turnos if t.fecha == fecha_dia]
            agenda_dias.append({
                "nombre": nombre,
                "fecha": fecha_dia,
                "manana": sorted(
                    [t for t in turnos_dia if t.hora < hora_limite_tarde], key=lambda t: t.hora
                ),
                "tarde": sorted(
                    [t for t in turnos_dia if t.hora >= hora_limite_tarde], key=lambda t: t.hora
                ),
            })

        profesional_nombre = self.get_profesional_nombre(profesional_id)
        titulo = f"Agenda semanal - {profesional_nombre}" if profesional_nombre else "Agenda semanal"
        filename = f"turnos_profesional_{profesional_id}_{lunes.isoformat()}.pdf"

        return self.render_turnos_pdf(agenda_dias, titulo, filename)

    def get_fecha_referencia(self, fecha):
        if not fecha:
            return date.today()
        try:
            return datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return date.today()

    def get_profesional_nombre(self, profesional_id):
        """Ajustar al método real de tu profesionalRepo."""
        if not profesional_id:
            return ""
        try:
            profesional = profesionalRepo.get_by_id(profesional_id)
            return f"{profesional.apellido}, {profesional.nombre}"
        except Exception:
            return ""


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoCreate(View):

    def get(self, request):
        form = TurnoCreateForm()
        return render(
            request,
            'turnos/create.html',
            dict(
                form=form,
            )
        )

    def post(self, request):
        form = TurnoCreateForm(request.POST)
        if form.is_valid():
            turnoRepo.create(
                paciente=form.cleaned_data['paciente_id'],
                profesional=form.cleaned_data['profesional_id'],
                tratamiento=form.cleaned_data['tratamiento_id'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                motivo=form.cleaned_data['motivo'],
            )
            return redirect('turnos_rehab')

        return render(
            request,
            'turnos/create.html',
            dict(
                form=form,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoUpdate(View):

    def get(self, request, id):
        turno = turnoRepo.get_by_id(id=id)
        print(turno)
        form = TurnoUpdateForm(instance=turno)
        return render(
            request,
            'turnos/update.html',
            dict(
                form=form,
            )
        )

    def post(self, request, id):
        turno = turnoRepo.get_by_id(id=id)
        form = TurnoUpdateForm(request.POST)
        if form.is_valid():
            turnoRepo.update(
                turno=turno,
                profesional=form.cleaned_data['profesional_id'],
                tratamiento=form.cleaned_data['tratamiento_id'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                motivo=form.cleaned_data['motivo'],
            )
            return redirect('turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoEstadoUpdate(View):

    def post(self, request, id):
        redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'turnos_rehab'
        turno = turnoRepo.get_by_id(id=id)
        if turno is None:
            return redirect(redirect_to)

        if turno.estado == turno.ESTADO_ANULADO:
            messages.error(request, 'El turno anulado no puede volver a editarse.')
            return redirect(redirect_to)

        accion = request.POST.get('accion')
        motivo_anulacion = request.POST.get('motivo_anulacion', '').strip()

        if accion == 'REALIZADO':
            turnoRepo.marcar_realizado(turno=turno)
        elif accion == 'ANULADO':
            if not motivo_anulacion:
                messages.error(request, 'El motivo de anulacion es obligatorio.')
                return redirect(redirect_to)
            turnoRepo.anular(
                turno=turno,
                motivo_anulacion=motivo_anulacion,
                usuario_anulacion=request.user,
            )

        return redirect(redirect_to)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class TurnoDelete(View):

    def get(self, request, id, *args, **kwargs):
        turno = turnoRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        turnoRepo.delete_by_activo(turno=turno)
        return redirect(request.META.get('HTTP_REFERER') or 'turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TurnoPacienteDetailRedirect(View):

    def get(self, request, id):
        prioridades = [
            (2, 'paciente_rehab_detail'),
            (3, 'paciente_fisiatria_detail'),
            (1, 'paciente_detail'),
        ]

        for area_id, url_name in prioridades:
            if pacienteAreaRepo.paciente_area_exist(id=id, area_id=area_id):
                return redirect(url_name, id)

        messages.error(request, 'No se encontro el paciente en Rehabilitacion, Fisiatria ni Gimnasio.')
        return redirect(request.META.get('HTTP_REFERER') or 'turnos_rehab')


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion", "Profesional"), name="dispatch")
class TratamientosPorProfesionalRehabView(View):

    def get(self, request, profesional_id):
        tratamientos_profesional = tratamientoProfesionalRepo.tratamientos_profesional_turnos(profesional_id=profesional_id)

        data = [
            {
                "id": item.id_tratamiento.id,
                "nombre": item.id_tratamiento.nombre,
            }
            for item in tratamientos_profesional
        ]
        return JsonResponse(data, safe=False)