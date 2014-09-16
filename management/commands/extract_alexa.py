# http://lxml.de/lxmlhtml.html
# http://lxml.de/cssselect.html

from lxml import html
import csv


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'List Alexa top 500 sites'

    def handle(self, **options):

        from HIF.input.http.core import HttpLink
        sites = []

        for link in HttpLink.objects.all().order_by('id'):
            root = html.fromstring(link.body)
            for el in root.cssselect('.site-listing a'):
                if el.text == "More":
                    continue
                sites.append(el.text)

        with open('alexa.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Link', 'Rank'])
            for rank, site in enumerate(sites):
                name = site[:site.find('.')]
                href = "http://{}".format(site.lower())
                writer.writerow([name, href, rank])

