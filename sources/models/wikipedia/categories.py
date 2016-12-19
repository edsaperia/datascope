from core.utils.helpers import override_dict

from sources.models.wikipedia.query import WikipediaGenerator


class WikipediaCategories(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categories",
        "gcllimit": 500,
        "gclshow": "!hidden",
        "prop": "info|pageprops|categoryinfo"
    })

    class Meta:
        verbose_name = "Wikipedia category"
        verbose_name_plural = "Wikipedia categories"


class WikipediaCategoryMembers(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categorymembers",
        "gcmlimit": 100,
        "gcmnamespace": 0,
        "prop": "info|pageprops|categories",
        "clshow": "!hidden",
        "cllimit": 500,
    })

    WIKI_QUERY_PARAM = "gcmtitle"

    class Meta:
        verbose_name = "Wikipedia category members"
        verbose_name_plural = "Wikipedia category members"
