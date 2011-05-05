from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson
from django.utils.translation import ugettext as _

from survey.forms import QuestionForm
from survey.models import Survey, Question, SurveyAnswer


def home(request, code):
    survey = get_object_or_404(Survey.objects.filter(is_active=True), code=code)
    return redirect(survey.answers.create())


def survey(request, survey_code, code):
    answer = get_object_or_404(SurveyAnswer,
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    try:
        data = simplejson.loads(answer.answers)
    except ValueError:
        data = {}

    kwargs = {
        'questions': Question.objects.filter(group__survey=answer.survey),
        'initial': data,
        }

    if request.method == 'POST':
        form = QuestionForm(request.POST, **kwargs)

        if form.is_valid():
            data.update(form.cleaned_data)

            answer.answers = simplejson.dumps(data)
            answer.save()

            return redirect(answer)

            # TODO redirection handling

    else:
        form = QuestionForm(**kwargs)

    return render(request, 'survey/form.html', {
        'survey': answer.survey,
        'form': form,
        })
