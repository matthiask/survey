from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from survey.forms import QuestionForm, SurveyEndForm
from survey.models import Survey, Question, SurveyAnswer


def home(request, code):
    survey = get_object_or_404(Survey.objects.filter(is_active=True), code=code)
    return redirect(survey.answers.create())


def survey(request, survey_code, code, page=1):
    answer = get_object_or_404(SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    pages = answer.survey.pages()

    # Only look at valid pages
    try:
        page = int(page)
        groups = pages[page - 1]
    except (IndexError, TypeError, ValueError):
        return redirect(answer)

    kwargs = {
        'questions': Question.objects.filter(group__in=groups).order_by(
            'group', 'ordering').select_related('group'),
        'answer': answer,
        }

    if request.method == 'POST':
        form = QuestionForm(request.POST, **kwargs)

        if form.is_valid():
            form.save()

            if 'finish' in request.POST:
                return redirect('survey.views.survey_end',
                    survey_code=survey_code,
                    code=code)
            elif 'prev' in request.POST:
                offset = -1
            else:
                offset = 1

            if 0 < page + offset <= len(pages):
                return redirect('survey.views.survey',
                    survey_code=survey_code,
                    code=code,
                    page=page + offset)

    else:
        form = QuestionForm(**kwargs)

    return render(request, 'survey/form.html', {
        'survey': answer.survey,
        'form': form,

        'page': page,
        'page_count': len(pages),
        'is_first_page': page == 1,
        'is_last_page': page == len(pages),
        })


def survey_end(request, survey_code, code):
    answer = get_object_or_404(SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    if request.method == 'POST':
        form = SurveyEndForm(request.POST, instance=answer)

        if form.is_valid():
            form.save()

            return redirect('survey.views.survey_thanks',
                    survey_code=survey_code,
                    code=code)
    else:
        form = SurveyEndForm(instance=answer)

    return render(request, 'survey/end.html', {
        'survey': answer.survey,
        'form': form,
        })


def survey_thanks(request, survey_code, code):
    answer = get_object_or_404(SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    return render(request, 'survey/thanks.html', {
        'survey': answer.survey,
        'answer': answer,
        })
