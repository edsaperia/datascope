from time import sleep
import random


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Scrape Alexa top 500 sites'

    def handle(self, **options):


        from HIF.input.http.core import HttpLink

        BASE_URL = "http://www.alexa.com/topsites/global;{}"
        MIN_SLEEP = 60
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        ]

        for ind in xrange(0, 20):

            url = BASE_URL.format(ind)

            ts = HttpLink()
            ts.request_headers.update({
                "User-Agent": USER_AGENTS[ind % len(USER_AGENTS)]
            })
            ts.url = url
            ts.get(ind)
            ts.save()

            print ts.url

            sleep(MIN_SLEEP + random.randint(0,11))