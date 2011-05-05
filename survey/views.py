from django import forms
from django.shortcuts import get_object_or_404, render

from survey.models import Survey, Question


class QuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuestionForm, self).__init__(*args, **kwargs)

        self._survey = []
        for question in questions:
            self._survey.append(self.add_question(question))

    def add_question(self, question):
        key = 'question_%s_%s' % (question.group_id, question.id)
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
                widget=forms.RadioSelect,
                **kwargs)
            keys['importance'] = key + '_imp'

        if question.type == question.YESNO:
            self.fields[key] = forms.ChoiceField(
                choices=[
                    ('1', _('Yes')),
                    ('0', _('No')),
                    ],
                widget=forms.RadioSelect,
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
                widget=forms.RadioSelect,
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
        for line in self._survey:
            yield dict((key, self[field]) for key, field in line.items())


def home(request, code):
    survey = get_object_or_404(Survey.objects.filter(is_active=True), code=code)


    if request.method == 'POST':
        form = QuestionForm(request.POST,
            questions=Question.objects.filter(group__survey=survey))

        if form.is_valid():
            import pprint
            pprint.pprint(form.cleaned_data)

    else:
        form = QuestionForm(
            questions=Question.objects.filter(group__survey=survey))

    return render(request, 'survey/form.html', {
        'survey': survey,
        'form': form,
        })
