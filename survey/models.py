import random
import string

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _


def generate_code():
    return u''.join([random.choice(string.letters+string.digits) for i in range(10)])


class Survey(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    title = models.CharField(_('title'), max_length=100)
    code = models.CharField(_('code'), max_length=20, default=generate_code)

    class Meta:
        verbose_name = _('survey')
        verbose_name_plural = _('surveys')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % self.code


class QuestionGroup(models.Model):
    survey = models.ForeignKey(Survey)
    ordering = models.IntegerField(_('ordering'), default=0)
    title = models.CharField(_('title'), max_length=100)

    class Meta:
        ordering = ['ordering']
        unique_together = (('survey', 'ordering'),)
        verbose_name = _('question group')
        verbose_name_plural = _('question groups')

    def __unicode__(self):
        return u'%s - %s' % (self.survey, self.title)


class Question(models.Model):
    YESNO = 'yesno'
    GRADE = 'grade'
    TEXT = 'text'
    CHECKBOX = 'checkbox'

    TYPE_CHOICES = (
        (YESNO, _('yes or no')),
        (GRADE, _('grade')),
        (TEXT, _('text')),
        (CHECKBOX, _('checkbox')),
        )

    group = models.ForeignKey(QuestionGroup)
    ordering = models.IntegerField(_('ordering'), default=0)

    text = models.CharField(_('question'), max_length=200)

    has_importance = models.BooleanField(_('has importance'), default=False)
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['ordering']
        unique_together = (('group', 'ordering'),)
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __unicode__(self):
        return self.text


class SurveyAnswer(models.Model):
    survey = models.ForeignKey(Survey)
    code = models.CharField(_('code'), max_length=20, default=generate_code)

