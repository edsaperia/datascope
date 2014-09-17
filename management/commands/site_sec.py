import csv

from django.core.management.base import BaseCommand

from HIF.helpers.data import find_row_in_csv


class Command(BaseCommand):
    help = 'Divide top 500 sites based on financial data'

    def write_csv_with_sec(self, file_name, rows):
        print "Writing: {}".format(file_name)
        columns = ['Name', 'Link', 'Rank', 'SEC-ticker', 'SEC-name', 'SEC-sector', 'SEC-industry']
        header = dict(zip(columns, columns))  # creates a dict where keys and values are columns
        with open(file_name, 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, columns)
            writer.writerows([header] + rows)  # adding header as a row


    def handle(self, **options):

        with open('alexa.csv', 'rb') as csvfile:

            reader = csv.DictReader(csvfile)
            extended_rows = []
            not_found_rows = []
            found_rows = []


            for row in reader:

                try:
                    rsl = find_row_in_csv(row['Name'], 'secwiki_tickers.csv')
                    row['SEC-ticker'] = rsl[0]
                    row['SEC-name'] = rsl[1]
                    row['SEC-sector'] = rsl[2]
                    row['SEC-industry'] = rsl[3]
                    found_rows.append(row)
                except IndexError:
                    not_found_rows.append(row)

                extended_rows.append(row)

        self.write_csv_with_sec('alexa+SEC.csv', extended_rows)
        self.write_csv_with_sec('alexa-with-SEC.csv', found_rows)
        self.write_csv_with_sec('alexa-without-SEC.csv', not_found_rows)
