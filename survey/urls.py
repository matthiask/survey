from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<code>[\w]+)/$', 'survey.views.home'),
    url(r'^(?P<code>[\w]+)/export/$', 'survey.views.survey_export'),
    url(r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/$', 'survey.views.survey'),
    url(r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/(?P<page>\d+)/$', 'survey.views.survey'),
    url(r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/end/$', 'survey.views.survey_end'),
    url(r'^(?P<survey_code>[\w]+)/(?P<code>[\w]+)/thanks/$', 'survey.views.survey_thanks'),
)
