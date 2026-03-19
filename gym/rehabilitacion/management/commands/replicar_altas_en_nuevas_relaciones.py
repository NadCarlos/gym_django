from django.core.management.base import BaseCommand
from django.db import transaction

from rehabilitacion.models import Alta, AltaEtiologico, AltaTipoDiscapacidad


class Command(BaseCommand):
    help = (
        'Replica la relación vieja de Alta -> DiagnosticoEtiologico '
        'en AltaEtiologico y AltaTipoDiscapacidad.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se crearía sin persistir cambios.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        creados_etiologicos = 0
        creados_tipos = 0
        existentes_etiologicos = 0
        existentes_tipos = 0

        altas = Alta.objects.select_related(
            'id_diagnostico_etiologico__id_tipo_discapacidad',
            'id_paciente_rehabilitacion__id_usuario',
        ).all()

        with transaction.atomic():
            for alta in altas:
                diagnostico_etiologico = alta.id_diagnostico_etiologico
                usuario = None
                if alta.id_paciente_rehabilitacion is not None:
                    usuario = alta.id_paciente_rehabilitacion.id_usuario

                if diagnostico_etiologico is not None:
                    alta_etiologico, created = AltaEtiologico.objects.get_or_create(
                        id_alta=alta,
                        id_diagnostico_etiologico=diagnostico_etiologico,
                        defaults={
                            'observaciones': '',
                            'activo': not alta.dado_alta,
                            'id_usuario': usuario,
                        },
                    )
                    if created:
                        creados_etiologicos += 1
                    else:
                        existentes_etiologicos += 1

                    tipo_discapacidad = diagnostico_etiologico.id_tipo_discapacidad
                    if tipo_discapacidad is not None:
                        alta_tipo_discapacidad, created = AltaTipoDiscapacidad.objects.get_or_create(
                            id_alta=alta,
                            id_tipo_discapacidad=tipo_discapacidad,
                            defaults={
                                'observaciones': '',
                                'activo': not alta.dado_alta,
                                'id_usuario': usuario,
                            },
                        )
                        if created:
                            creados_tipos += 1
                        else:
                            existentes_tipos += 1

            if dry_run:
                transaction.set_rollback(True)

        modo = 'DRY RUN' if dry_run else 'EJECUTADO'
        self.stdout.write(self.style.SUCCESS(f'[{modo}] Altas procesadas: {altas.count()}'))
        self.stdout.write(self.style.SUCCESS(f'[{modo}] AltaEtiologico creados: {creados_etiologicos}'))
        self.stdout.write(self.style.SUCCESS(f'[{modo}] AltaTipoDiscapacidad creados: {creados_tipos}'))
        self.stdout.write(f'[{modo}] AltaEtiologico ya existentes: {existentes_etiologicos}')
        self.stdout.write(f'[{modo}] AltaTipoDiscapacidad ya existentes: {existentes_tipos}')
