import csv

from django.core.management.base import BaseCommand

from HIF.helpers.data import find_row_in_csv


class Command(BaseCommand):
    help = 'Divide top 500 sites based on financial data'

    def write_csv_with_sec(self, file_name, rows):
        print "Writing: {}".format(file_name)
        columns = ['Site', 'Rang', 'Moederbedrijf', 'Page Views', 'Page duration', 'Bubble index']
        header = dict(zip(columns, columns))  # creates a dict where keys and values are columns
        with open(file_name, 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, columns)
            writer.writerows([header] + rows)  # adding header as a row


    def handle(self, **options):

        with open('sites-list.csv', 'rb') as csvfile:

            reader = csv.DictReader(csvfile)
            listing = []

            for row in reader:

                try:
                    rsl = find_row_in_csv(row['Moederbedrijf'], 'mother-companies.csv')
                    row['Bubble index'] = rsl[6]
                except IndexError:
                    row['Bubble index'] = 0

                row['Rang'] = int(row['Rang']) + 1
                listing.append(row)

        self.write_csv_with_sec('crash-list.csv', listing)
        #self.write_csv_with_sec('alexa-with-SEC.csv', found_rows)
        #self.write_csv_with_sec('alexa-without-SEC.csv', not_found_rows)
