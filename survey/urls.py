from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(
        r'^(?P<code>[\w]+)/$',
        'survey.views.home',
        name='survey_home',
    ),
    url(
        r'^(?P<code>[\w]+)/export/$',
        'survey.views.survey_export',
        name='survey_export',
    ),
    url(
        r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/$',
        'survey.views.survey',
        name='survey_survey_start',
    ),
    url(
        r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/(?P<page>\d+)/$',
        'survey.views.survey',
        name='survey_survey_page',
    ),
    url(
        r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/end/$',
        'survey.views.survey_end',
        name='survey_survey_end',
    ),
    url(
        r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/thanks/$',
        'survey.views.survey_thanks',
        name='survey_survey_thanks',
    ),
)
