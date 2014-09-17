import csv

from django.core.management.base import BaseCommand

from HIF.helpers.data import find_row_in_csv



class Command(BaseCommand):
    help = 'Process data to csv file'



    def handle(self, **options):
        from HIF.processes.core import Process

        columns = ['Name', 'Link', 'Rank', 'SEC-ticker', 'SEC-name', 'SEC-sector', 'SEC-industry', 'Net Income', 'Stock Price (end of year)']
        header = dict(zip(columns, columns))  # creates a dict where keys and values are columns

        with open('test-output.csv', 'wb') as csvfile:

            writer = csv.DictWriter(csvfile, columns)
            prc = Process()
            prc.load(serialization=['ProcessStorage', 1])
            writer.writerows([header] + prc.rsl)  # adding header as a row

