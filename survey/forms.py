from django import forms
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from survey.models import SurveyAnswer

class CustomRadioRenderer(forms.widgets.RadioFieldRenderer):
    def render(self):
        return mark_safe(u'\n'.join(force_unicode(w) for w in self))


class CustomRadioSelect(forms.widgets.RadioSelect):
    renderer = CustomRadioRenderer


class QuestionForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        self.questions = list(kwargs.pop('questions'))
        self.answer = kwargs.pop('answer')

        try:
            kwargs['initial'] = self._answers = simplejson.loads(self.answer.answers)
        except ValueError:
            self._answers = {}

        super(QuestionForm, self).__init__(*args, **kwargs)

        self._survey = []
        for question in self.questions:
            self._survey.append((question, self.add_question(question)))

    def save(self):
        self._answers.update(self.cleaned_data)
        self.answer.answers = simplejson.dumps(self._answers)
        self.answer.save()

    def add_question(self, question):
        key = 'q_%s_%s' % (question.group_id, question.id)
        keys = {'answer': key}

        kwargs = {
            'required': False,
            'label': question.text,
            }

        if question.has_importance:
            self.fields[key + '_imp'] = forms.ChoiceField(
                choices=[
                    ('1', ''),
                    ('2', ''),
                    ('3', ''),
                    ('4', ''),
                    ('u', ''),
                    ],
                widget=CustomRadioSelect,
                **kwargs)
            keys['importance'] = key + '_imp'

        if question.type == question.YESNO:
            self.fields[key] = forms.ChoiceField(
                choices=[
                    ('1', _('Yes')),
                    ('0', _('No')),
                    ],
                widget=CustomRadioSelect,
                **kwargs)
        elif question.type == question.GRADE:
            self.fields[key] = forms.ChoiceField(
                choices=[
                    ('1', ''),
                    ('2', ''),
                    ('3', ''),
                    ('4', ''),
                    ('u', ''),
                    ],
                widget=CustomRadioSelect,
                **kwargs)
        elif question.type == question.TEXT:
            self.fields[key] = forms.CharField(
                widget=forms.Textarea,
                **kwargs)
        elif question.type == question.CHECKBOX:
            self.fields[key] = forms.BooleanField(
                **kwargs)
        else:
            raise NotImplementedError

        return keys

    def survey_fields(self):
        for question, line in self._survey:
            yield question, dict((key, self[field]) for key, field in line.items())


class SurveyEndForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = SurveyAnswer
        fields = ('visitor_company', 'visitor_name', 'visitor_contact')
