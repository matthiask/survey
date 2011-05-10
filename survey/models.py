import random
import string

from django import forms
from django.db import models
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _


def generate_code():
    return u''.join([random.choice(string.letters+string.digits) for i in range(10)])


class Survey(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    title = models.CharField(_('title'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True,
        default=generate_code)

    class Meta:
        verbose_name = _('survey')
        verbose_name_plural = _('surveys')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % self.code

    def pages(self):
        pages = [[]]
        for group in self.groups.all():
            if group.new_page:
                pages.append([])
            pages[-1].append(group)

        # Remove first page if it is empty
        if not pages[0]:
            pages = pages[1:]

        return pages


class QuestionGroup(models.Model):
    survey = models.ForeignKey(Survey, related_name='groups',
        verbose_name=_('survey'))
    ordering = models.IntegerField(_('ordering'), default=0)
    title = models.CharField(_('title'), max_length=100)
    new_page = models.BooleanField(_('starts new page'), default=False)

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
    INITIAL = 0
    INVITED = 5
    STARTED = 10
    FINISHED = 15
    COMPLETED = 20

    STATUS_CHOICES = (
        (INITIAL, _('initial state')),
        (INVITED, _('invited')),
        (STARTED, _('started')),
        (FINISHED, _('finished')),
        (COMPLETED, _('completed')),
        )

    survey = models.ForeignKey(Survey, related_name='answers',
        verbose_name=_('survey'))
    code = models.CharField(_('code'), max_length=20, default=generate_code)
    status = models.PositiveIntegerField(_('status'), choices=STATUS_CHOICES,
        default=INITIAL)

    answers = models.TextField(_('answers'), blank=True)

    visitor_company = models.CharField(_('company'), max_length=100, blank=True)
    visitor_name = models.CharField(_('name'), max_length=100, blank=True)
    visitor_contact = models.CharField(_('contact'), max_length=100)

    visitor_counter = models.PositiveIntegerField(_('visitor counter'), default=0)

    conductor_company = models.CharField(_('company'), max_length=100, blank=True)
    conductor_name = models.CharField(_('name'), max_length=100, blank=True)
    conductor_contact = models.CharField(_('contact'), max_length=100, blank=True)

    class Meta:
        unique_together = (('survey', 'code'),)
        verbose_name = _('survey answer')
        verbose_name_plural = _('survey answers')

    def __unicode__(self):
        return u'Survey %s answered by %s' % (self.survey, self.visitor_contact)

    def get_absolute_url(self):
        return u'%s%s/' % (self.survey.get_absolute_url(), self.code)

    def details(self):
        try:
            data = simplejson.loads(self.answers)
        except ValueError:
            data = {}

        for question in Question.objects.filter(group__survey=self.survey).order_by(
                'group', 'ordering').select_related('group'):

            key = 'q_%s_%s' % (question.group_id, question.id)
            answers = {
                'answer': data.get(key),
                'importance': data.get(key + '_imp'),
                }

            yield question, answers

    def update_status(self, status):
        if self.status < status:
            self.status = status
            self.save()
