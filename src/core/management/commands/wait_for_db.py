"""Responsável por aguardar o database estar disponível"""

import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Aguarda a execução do database"""

    def handle(self, *args, **options):
        "Entrypoint dos comandos"
        self.stdout.write(self.style.WARNING('Info: Waiting for database...'))
        db_up = False

        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(self.style.ERROR(
                    'Error: Database unavailable, waiting 1 second...'))
                time.sleep(1)
            finally:
                self.stdout.write(self.style.SUCCESS(
                    'Success: Database available!'))
