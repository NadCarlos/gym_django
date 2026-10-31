from datetime import date
from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
from django import forms
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import storages
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase
from openpyxl import load_workbook


class UpgradeCompatibilityTests(SimpleTestCase):
    def test_excel_import_rejects_xml_entities(self):
        original = BytesIO()
        with pd.ExcelWriter(original, engine="xlsxwriter") as writer:
            pd.DataFrame({"Paciente": ["safe-marker"]}).to_excel(writer, index=False)
        crafted = BytesIO()
        with ZipFile(original) as source, ZipFile(crafted, "w") as target:
            for item in source.infolist():
                content = source.read(item.filename)
                if item.filename == "xl/sharedStrings.xml":
                    # One harmless entity exercises the real import path without
                    # allocating a large payload or contacting an external host.
                    declaration = b'<!DOCTYPE sst [<!ENTITY sample "expanded-marker">]>'
                    content = content.replace(b"?>", b"?>" + declaration, 1)
                    content = content.replace(b"safe-marker", b"&sample;")
                target.writestr(item, content)
        crafted.seek(0)
        with self.assertRaises(ValueError) as caught:
            pd.read_excel(crafted)
        from defusedxml.common import EntitiesForbidden

        self.assertIsInstance(caught.exception.__cause__, EntitiesForbidden)

    def test_existing_template_number_and_date_output_is_preserved(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        template = Template(
            '{% extends "home/base.html" %}{% block content %}'
            'amount={{ amount }};day={{ day }};'
            'hours={{ hours|floatformat:2 }};{% endblock %}'
        )
        html = template.render(Context({
            "request": request,
            "user": request.user,
            "amount": Decimal("1234.56"),
            "day": date(2026, 10, 24),
            "hours": Decimal("1.25"),
        }))
        self.assertIn("amount=1234.56;day=24/10/2026;hours=1,25;", html)

    def test_default_date_inputs_keep_the_previous_formats(self):
        field = forms.DateField()
        self.assertEqual(field.clean("2026-10-24"), date(2026, 10, 24))
        self.assertEqual(field.clean("10/24/2026"), date(2026, 10, 24))

    def test_backups_remain_outside_public_media_storage(self):
        backup_storage = storages["dbbackup"]
        self.assertEqual(backup_storage.location, str(settings.BASE_DIR / "backup_data"))
        self.assertNotEqual(backup_storage.location, storages["default"].location)

    def test_excel_export_round_trip_preserves_values_and_dates(self):
        output = BytesIO()
        data = pd.DataFrame({
            "Paciente": ["Pérez, Ana"],
            "Fecha": [date(2026, 10, 24)],
            "Importe": [1234.56],
        })
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            data.to_excel(writer, index=False)
        output.seek(0)
        workbook = load_workbook(output, read_only=True, data_only=True)
        try:
            row = list(workbook.active.values)[1]
            self.assertEqual(row[0], "Pérez, Ana")
            self.assertEqual(row[1].date(), date(2026, 10, 24))
            self.assertEqual(row[2], 1234.56)
        finally:
            workbook.close()
