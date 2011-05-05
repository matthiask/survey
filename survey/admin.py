from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from survey import models


class QuestionGroupInline(admin.TabularInline):
    model = models.QuestionGroup
    extra = 0

class QuestionInline(admin.TabularInline):
    model = models.Question
    extra = 0


admin.site.register(models.Survey,
    inlines=[QuestionGroupInline],
    list_display=('is_active', 'title', 'code'),
    list_display_links=('title',),
    list_filter=('is_active',),
    )
admin.site.register(models.QuestionGroup,
    inlines=[QuestionInline],
    list_display=('survey', 'ordering', 'title'),
    list_display_links=('title',),
    list_filter=('survey',),
    )
admin.site.register(models.Question,
    list_display=('group', 'ordering', 'text', 'has_importance', 'type'),
    list_display_links=('text',),
    list_filter=('group__survey',),
    )

admin.site.register(models.SurveyAnswer,
    fieldsets=(
        (None, {
            'fields': ('survey', 'code', 'status'),
        }),
        (_('Visitor'), {
            'fields': (('visitor_company', 'visitor_name', 'visitor_contact'),),
        }),
        (_('Conductor'), {
            'fields': (('conductor_company', 'conductor_name', 'conductor_contact'),),
        }),
        (_('Answers'), {
            'fields': ('answers',),
            'classes': ('collapse',),
        }),
        ),
    list_display=('survey', 'status', 'code', 'visitor_name', 'visitor_contact'),
    list_display_links=('code',),
    list_filter=('survey', 'status', 'conductor_name'),
    )
