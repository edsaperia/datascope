from django.conf.urls import patterns, url

from legacy.output.http.services.manifests import (VisualTranslationsService, PeopleSuggestionsService,
                                                 CityCelebritiesService, PopularityComparisonService)


urlpatterns = patterns('legacy.views',
    url(r'^visual-translations/?$', VisualTranslationsService.HIF_main.as_view(), {"Service": VisualTranslationsService}, name='visual-translations'),
    url(r'^visual-translations/plain/?$', VisualTranslationsService.HIF_plain.as_view(), {"Service": VisualTranslationsService}, name='visual-translations-plain'),

    url(r'^people-suggestions/?$', PeopleSuggestionsService.HIF_main.as_view(), {"Service": PeopleSuggestionsService}, name='people-suggestions'),
    url(r'^people-suggestions/plain/?$', PeopleSuggestionsService.HIF_plain.as_view(), {"Service": PeopleSuggestionsService}, name='people-suggestions-plain'),

    url(r'^city-celebrities/?$', CityCelebritiesService.HIF_main.as_view(), {"Service": CityCelebritiesService}, name='city-celebrities'),

    url(r'^popularity-comparison/?$', PopularityComparisonService.HIF_main.as_view(), {"Service": PopularityComparisonService}, name='popularity-comparison'),

    url(r'question/?', 'question', name='question')
)