import csv

from django.core.management.base import BaseCommand

from HIF.helpers.data import find_row_in_csv



class Command(BaseCommand):
    help = 'Store rows in Process object'

    def handle(self, **options):
        from HIF.processes.core import Process

        with open('test-rows.csv', 'rb') as csvfile:

            reader = csv.DictReader(csvfile)
            prc = Process()
            prc.setup('rows')
            prc.results = list(reader)
            prc.save()

