from __future__ import unicode_literals, absolute_import, print_function, division
import six

from collections import OrderedDict
from itertools import groupby
from copy import copy

from core.models.organisms import Community, Collective, Individual
from core.utils.image import ImageGrid
from core.processors.expansion import ExpansionProcessor

from sources.models.downloads import ImageDownload


class VisualTranslationsEUCommunity(Community):

    COMMUNITY_NAME = "visual_translations_eu"

    COMMUNITY_SPIRIT = OrderedDict([
        ("translations", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["translate_from", "$.translate_to", "$.query"],
                "_kwargs": {},
                "_resource": "GoogleTranslate",
                "_objective": {
                    "@": "$",
                    "language": "$.language",
                    "word": "$.word",
                    "confidence": "$.confidence",
                    "meanings": "$.meanings"
                },
                "_interval_duration": 2500
            },
            "schema": {},
            "errors": {},
        }),
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@translations",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.word", "$.country"],
                "_kwargs": {},
                "_resource": "GoogleImage",
                "_objective": {
                    "@": "$.items",
                    "#word": "$.queries.request.0.searchTerms",
                    "#country": "$.queries.request.0.cr",
                    "url": "$.link",
                    "width": "$.image.width",
                    "height": "$.image.height",
                    "thumbnail": "$.image.thumbnailLink",
                },
            },
            "schema": {},
            "errors": {},
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@images",
            "contribute": None,
            "output": None,
            "config": {
                "_args": ["$.url"],
                "_kwargs": {},
                "_resource": "ImageDownload"
            },
            "schema": {},
            "errors": None,
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "ExpansionProcessor.collective_content",
            "config": {}
        }
    ]

    LOCALES = [
        ("de", "AT", {"columns": 4, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("nl", "BE", {"columns": 5, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("fr", "BE", {"columns": 5, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("bg", "BG", {"columns": 4, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("hr", "HR", {"columns": 6, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("el", "CY", {"columns": 2, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("cs", "CZ", {"columns": 4, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("da", "DK", {"columns": 2, "rows": 5, "cell_width": 80, "cell_height": 45}, 3,),
        ("et", "EE", {"columns": 3, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("fi", "FI", {"columns": 3, "rows": 6, "cell_width": 320, "cell_height": 180}, 1,),
        ("fr", "FR", {"columns": 4, "rows": 4, "cell_width": 320, "cell_height": 180}, 1,),
        ("de", "DE", {"columns": 4, "rows": 4, "cell_width": 320, "cell_height": 180}, 1,),
        ("el", "GR", {"columns": 2, "rows": 5, "cell_width": 80, "cell_height": 45}, 3,),
        ("hu", "HU", {"columns": 4, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("it", "IT", {"columns": 4, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("lt", "LT", {"columns": 3, "rows": 3, "cell_width": 160, "cell_height": 90}, 2,),
        ("lv", "LV", {"columns": 5, "rows": 2, "cell_width": 160, "cell_height": 90}, 2,),
        ("fr", "LU", {"columns": 2, "rows": 2, "cell_width": 80, "cell_height": 45}, 1,),
        ("mt", "MT", {"columns": 2, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("nl", "NL", {"columns": 4, "rows": 8, "cell_width": 80, "cell_height": 45}, 3),
        ("pl", "PL", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180}, 1,),
        ("pt", "PT", {"columns": 2, "rows": 6, "cell_width": 80, "cell_height": 45}, 2,),
        ("ro", "RO", {"columns": 4, "rows": 4, "cell_width": 160, "cell_height": 90}, 2,),
        ("sl", "SI", {"columns": 3, "rows": 3, "cell_width": 80, "cell_height": 45}, 2,),
        ("es", "ES", {"columns": 4, "rows": 4, "cell_width": 320, "cell_height": 180}, 1,),
        ("sv", "SE", {"columns": 3, "rows": 6, "cell_width": 320, "cell_height": 180}, 1,),
        ("sk", "SK", {"columns": 6, "rows": 2, "cell_width": 80, "cell_height": 45}, 2,),
        ("en", "GB", {"columns": 3, "rows": 6, "cell_width": 160, "cell_height": 90}, 2,),
        ("en", "IR", {"columns": 3, "rows": 4, "cell_width": 80, "cell_height": 45}, 3,),
    ]

    # TODO: don't hard code the source language

    def initial_input(self, *args):
        collective = Collective.objects.create(
            community=self,
            schema={}
        )
        query = args[0]
        # TODO: create dir here
        for language, country, grid, factor in self.LOCALES:
            if language == "en":
                continue
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "query": query,
                    "translate_from": "en",
                    "translate_to": language,
                    "country": "country" + country
                },
                schema={}
            )
        return collective

    def finish_translations(self, out, err):
        new = []
        group_lambda = lambda el: el[0]
        for group, values in groupby(sorted(self.LOCALES, key=group_lambda), group_lambda):
            locales = list(values)

            individuals = out.individual_set.all()
            for index, value in enumerate(locales):
                language, country, grid, factor = value

                if language == "en":  # creating individuals for untranslated words
                    translations = self.growth_set.filter(type="translations").last()
                    inp = translations.input.individual_set.first()
                    new.append({
                        "country": "country" + country,
                        "language": "en",
                        "word": inp.properties["query"],
                        "confidence": None,
                        "meanings": None,
                        "locale": "{}_{}".format(language, country)
                    })
                elif index == 0:  # only an update needed
                    for ind in individuals:  # TODO: simplify by using Collective.select (re-use querysets!)
                        if ind.properties["language"] != language:
                            continue
                        ind.properties["country"] = "country" + country
                        ind.properties["locale"] = "{}_{}".format(language, country)
                        new.append(ind)
                else:  # new individuals need to be created
                    for ind in individuals:  # TODO: simplify by using Collective.select (re-use querysets!)
                        if ind.properties["language"] != language:
                            continue
                        properties = copy(ind.properties)
                        properties["country"] = "country" + country
                        properties["locale"] = "{}_{}".format(language, country)
                        new.append(properties)
        if new:
            out.update(new)

    def finish_images(self, out, err):
        translations = self.growth_set.filter(type="translations").last()
        grouped_images = out.group_by("word")
        for ind in translations.output.individual_set.all():
            images = [
                image for image in grouped_images.get(ind.properties["word"], [])
                if image.properties["country"] == ind.properties["country"]
            ]
            if not images:
                translations.output.individual_set.remove(ind)
                continue

            col = Collective.objects.create(
                community=self,
                schema=out.schema
            )
            col.update(images)
            ind.properties["images"] = col.url
            ind.save()

    zoom_levels = {"S": 0.2, "L": 1, "XL": 1}

    def finish_download(self, out, err):  # TODO: move images in downloads folder? another way?
        translation_growth = self.growth_set.filter(type="translations").last()
        grids = {"{}_{}".format(language, country): (grid, factor) for language, country, grid, factor in self.LOCALES}
        grouped_translations = translation_growth.output.group_by("locale")
        for locale, translations in six.iteritems(grouped_translations):
            expansion_processor = ExpansionProcessor(self.config.to_dict())
            translations = expansion_processor.collective_content(
                [translation.properties for translation in translations]
            )
            images = []
            query = translation_growth.input.individual_set.last().properties["query"]
            for translation in translations:
                for image in translation["images"]:
                    images.append(image)
            downloads_queryset = ImageDownload.objects.filter(
                uri__in=[ImageDownload.uri_from_url(image["url"]) for image in images]
            )
            downloads = []
            for download in downloads_queryset:
                content_type, image = download.content
                if image is not None:
                    downloads.append(image)
            for size, factor in six.iteritems(self.zoom_levels):
                grid, xlarge_factor = grids[locale]
                factor = factor if size != "XL" else xlarge_factor
                grid_specs = copy(grid)
                grid_specs["cell_width"] = int(grid_specs["cell_width"] * factor)
                grid_specs["cell_height"] = int(grid_specs["cell_height"] * factor)
                image_grid = ImageGrid(**grid_specs)
                image_grid.fill(downloads)
                image_grid.export("visual_translations/{}/{}_{}.jpg".format(query, size, locale))

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="translations").last().output

    class Meta:
        verbose_name = "Visual translation (EU)"
        verbose_name_plural = "Visual translations (EU)"