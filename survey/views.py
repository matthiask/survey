from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from survey.forms import QuestionForm
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

            if 'next' in request.POST:
                offset = 1
            elif 'prev' in request.POST:
                offset = -1

            if 0 < page + offset <= len(pages):
                return redirect('survey.views.survey',
                    survey_code=survey_code,
                    code=code,
                    page=page + offset)

            # TODO send to thank you page

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
