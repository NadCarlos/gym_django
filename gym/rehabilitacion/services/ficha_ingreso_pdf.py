from io import BytesIO

from django.contrib.staticfiles import finders
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def _text(value):
    if value is None:
        return ""
    value = str(value).strip()
    return "" if value.lower() in {"none", "null"} else value


def _related_name(instance, attribute):
    related = getattr(instance, attribute, None)
    return _text(getattr(related, "nombre", ""))


def _date(value):
    return value.strftime("%d/%m/%Y") if value else ""


def _stored_value(value):
    """Oculta valores históricos usados como marcadores de campo vacío."""
    value = _text(value)
    return "" if value.upper() in {"NO", "0"} else value


def build_ficha_fields(paciente, rehabilitacion=None):
    obra_social = ""
    if rehabilitacion is not None:
        obra_social = _related_name(rehabilitacion, "id_obra_social")
    obra_social = obra_social or _related_name(paciente, "id_obra_social")

    estado_certificado = (
        _related_name(rehabilitacion, "id_estado_certificado").upper()
        if rehabilitacion is not None
        else ""
    )
    certificado_si = estado_certificado in {"SI", "SÍ"}
    certificado_no = estado_certificado == "NO"

    return {
        "nombre_completo": ", ".join(
            value for value in [_text(paciente.apellido), _text(paciente.nombre)] if value
        ),
        "dni": _text(paciente.numero_dni),
        "sexo": _related_name(paciente, "id_sexo"),
        "fecha_nacimiento": _date(paciente.fecha_nacimiento),
        "estado_civil": _related_name(paciente, "id_estado_civil"),
        "telefono": _text(paciente.telefono),
        "telefono_alternativo": _text(paciente.celular),
        "direccion": _text(paciente.direccion),
        "localidad": _related_name(paciente, "id_localidad"),
        "obra_social": obra_social,
        "numero_afiliado": _stored_value(
            getattr(rehabilitacion, "numero_afiliado", "")
        ),
        "certificado_si": certificado_si,
        "certificado_no": certificado_no,
        "vencimiento_certificado": _date(
            getattr(rehabilitacion, "vencimiento_certificado", None)
        ),
        "nombre_responsable": _stored_value(
            getattr(rehabilitacion, "nombre_tutor", "")
        ),
        "telefono_responsable": _text(
            getattr(rehabilitacion, "celular_tutor", "")
        ),
        "como_contacto": (
            _related_name(rehabilitacion, "id_conocer")
            if rehabilitacion is not None
            else ""
        ),
    }


class FichaIngresoPDF:
    margin_x = 1.7 * cm
    page_width, page_height = A4
    content_width = page_width - (2 * margin_x)

    def __init__(self, fields, generated_on):
        self.fields = fields
        self.generated_on = generated_on
        self.buffer = BytesIO()
        self.pdf = canvas.Canvas(self.buffer, pagesize=A4)
        self.pdf.setTitle("Ficha de ingreso")

    def build(self):
        self._header()
        self._personal_data()
        self._address_data()
        self._other_data()
        self._responsible_data()
        self._additional_information()
        self._footer()
        self.pdf.showPage()
        self.pdf.save()
        return self.buffer.getvalue()

    def _header(self):
        header_y = 27.25 * cm
        header_height = 2 * cm
        self.pdf.setFillColor(colors.HexColor("#ffffff"))
        self.pdf.rect(
            self.margin_x,
            header_y,
            self.content_width,
            header_height,
            stroke=0,
            fill=1,
        )
        logo_path = finders.find("public/cermed_sin_fondo.png")
        if logo_path:
            self.pdf.drawImage(
                logo_path,
                self.margin_x + 0.08 * cm,
                header_y + 0.05 * cm,
                width=1.9 * cm,
                height=1.9 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        self.pdf.setFillColor(colors.black)
        self.pdf.setFont("Helvetica-Bold", 14)
        self.pdf.drawCentredString(self.page_width / 2, 28.25 * cm, "FICHA DE INGRESO")
        self.pdf.setFont("Helvetica", 9)
        self.pdf.drawRightString(
            self.page_width - self.margin_x - 0.18 * cm,
            27.65 * cm,
            f"Fecha: {self.generated_on.strftime('%d/%m/%Y')}",
        )

    def _section(self, title, y):
        self.pdf.setFillColorRGB(0.85, 0.85, 0.85)
        self.pdf.rect(self.margin_x, y - 0.05 * cm, self.content_width, 0.65 * cm, fill=1)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.setFont("Helvetica-Bold", 9)
        self.pdf.drawString(self.margin_x + 0.18 * cm, y + 0.16 * cm, title)

    def _line_field(self, label, value, x, y, width, label_width=None):
        self.pdf.setFont("Helvetica", 9)
        self.pdf.drawString(x, y, label)
        label_width = label_width or stringWidth(label, "Helvetica", 9) + 0.15 * cm
        value_x = x + label_width
        self.pdf.line(value_x, y - 0.08 * cm, x + width, y - 0.08 * cm)
        self._fit_text(value, value_x + 0.08 * cm, y + 0.03 * cm, width - label_width - 0.16 * cm)

    def _fit_text(self, value, x, y, max_width, size=9):
        value = _text(value)
        while value and stringWidth(value, "Helvetica", size) > max_width:
            value = value[:-1]
        self.pdf.setFont("Helvetica", size)
        self.pdf.drawString(x, y, value)

    def _checkbox(self, x, y, label, checked=False):
        box = 0.28 * cm
        self.pdf.rect(x, y - 0.05 * cm, box, box, fill=0)
        if checked:
            self.pdf.setFont("Helvetica-Bold", 9)
            self.pdf.drawCentredString(x + box / 2, y, "X")
        self.pdf.setFont("Helvetica", 8.5)
        self.pdf.drawString(x + box + 0.1 * cm, y, label)

    def _personal_data(self):
        self._section("DATOS PERSONALES", 26.55 * cm)
        self._line_field("Apellido, Nombres", self.fields["nombre_completo"], self.margin_x, 25.5 * cm, self.content_width)
        self._line_field("DNI (Tipo y Nro.)", self.fields["dni"], self.margin_x, 24.55 * cm, 8.4 * cm)
        self.pdf.setFont("Helvetica", 9)
        self.pdf.drawString(10.5 * cm, 24.55 * cm, "Sexo")
        sexo = self.fields["sexo"].lower()
        self._checkbox(12 * cm, 24.52 * cm, "Femenino", "femen" in sexo)
        self._checkbox(15.2 * cm, 24.52 * cm, "Masculino", "mascul" in sexo)
        self._line_field("Fecha de Nacimiento", self.fields["fecha_nacimiento"], self.margin_x, 23.55 * cm, 8.4 * cm)
        self.pdf.setFont("Helvetica", 9)
        self.pdf.drawString(10.5 * cm, 23.55 * cm, "Estado Civil")
        estado = self.fields["estado_civil"].lower()
        for x, label in [(12.5, "Soltero"), (14.45, "Casado"), (16.35, "Divorciado"), (18.65, "Viudo")]:
            self._checkbox(x * cm, 23.52 * cm, label, label.lower() in estado)
        self._line_field("Teléfono", self.fields["telefono"], self.margin_x, 22.55 * cm, 8.4 * cm)
        self._line_field("Teléfono Alternativo", self.fields["telefono_alternativo"], 10.5 * cm, 22.55 * cm, 8.8 * cm)

    def _address_data(self):
        self._section("DATOS DE DOMICILIO", 21.35 * cm)
        self._line_field("Dirección", self.fields["direccion"], self.margin_x, 20.3 * cm, self.content_width)
        self._line_field("Localidad", self.fields["localidad"], self.margin_x, 19.3 * cm, self.content_width)

    def _other_data(self):
        self._section("OTROS DATOS", 18.1 * cm)
        self._line_field("OBRA SOCIAL", self.fields["obra_social"], self.margin_x, 17.05 * cm, 11.5 * cm)
        self._line_field("Afiliado N.º", self.fields["numero_afiliado"], 13.5 * cm, 17.05 * cm, 5.8 * cm)
        self.pdf.setFont("Helvetica", 9)
        self.pdf.drawString(self.margin_x, 15.85 * cm, "Certificado de Discapacidad")
        self._checkbox(7.5 * cm, 15.82 * cm, "SÍ", self.fields["certificado_si"])
        self._checkbox(9.2 * cm, 15.82 * cm, "NO", self.fields["certificado_no"])
        self._line_field("Vencimiento/Validez", self.fields["vencimiento_certificado"], 11.2 * cm, 15.85 * cm, 8.1 * cm)

    def _responsible_data(self):
        self._section("DATOS DEL ACOMPAÑANTE RESPONSABLE", 14.65 * cm)
        self._line_field("Apellido, Nombres", self.fields["nombre_responsable"], self.margin_x, 13.6 * cm, self.content_width)
        self._line_field("Teléfono", self.fields["telefono_responsable"], self.margin_x, 12.6 * cm, self.content_width)
        self._line_field("¿Cómo contacto?", self.fields["como_contacto"], self.margin_x, 11.35 * cm, self.content_width)

    def _additional_information(self):
        section_y = 10.15 * cm
        box_bottom = 2.2 * cm
        box_top = section_y - 0.15 * cm
        self._section("INFORMACIÓN ADICIONAL", section_y)
        self.pdf.setStrokeColor(colors.HexColor("#6c757d"))
        self.pdf.setLineWidth(0.6)
        self.pdf.rect(
            self.margin_x,
            box_bottom,
            self.content_width,
            box_top - box_bottom,
            stroke=1,
            fill=0,
        )
        line_y = box_top - 0.72 * cm
        while line_y > box_bottom:
            self.pdf.line(
                self.margin_x + 0.2 * cm,
                line_y,
                self.page_width - self.margin_x - 0.2 * cm,
                line_y,
            )
            line_y -= 0.72 * cm
        self.pdf.setStrokeColor(colors.black)

    def _footer(self):
        footer_y = 0.6 * cm
        icon_path = finders.find("public/logoiteclabs.png")
        self.pdf.saveState()
        self.pdf.setFont("Helvetica", 10)
        self.pdf.setFillColor(colors.HexColor("#6c757d"))
        if icon_path:
            icon_size = 1.5 * cm
            self.pdf.drawImage(
                icon_path,
                self.margin_x,
                footer_y - 0.20 * cm,
                width=icon_size,
                height=icon_size,
                preserveAspectRatio=True,
                mask="auto",
            )
        self.pdf.drawString(
            self.margin_x + 0.45 * cm,
            footer_y,
            "           Sistema ASISPRO powered by ITEClabs",
        )
        self.pdf.drawRightString(
            self.page_width - self.margin_x,
            footer_y,
            f"Rio Cuarto el {self._long_date(self.generated_on)}",
        )
        self.pdf.restoreState()

    @staticmethod
    def _long_date(value):
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


def render_ficha_ingreso_pdf(paciente, rehabilitacion, generated_on):
    fields = build_ficha_fields(paciente, rehabilitacion)
    return FichaIngresoPDF(fields, generated_on).build()
