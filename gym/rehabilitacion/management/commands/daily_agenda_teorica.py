from django.core.management.base import BaseCommand
from datetime import date

class Command(BaseCommand):
    help = "Agenda Teorica Diaria"

    def handle(self, *args, **options):
        today = date.today()
        self.stdout.write(
            self.style.SUCCESS(f"Tarea diaria ejecutada: {today}")
        )

        print("saas")