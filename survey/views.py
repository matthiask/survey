import StringIO
import xlwt

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import six
from django.utils.translation import ugettext as _

from survey.forms import QuestionForm, SurveyEndForm
from survey.models import Survey, Question, SurveyAnswer


if six.PY3:
    unicode = str


def increment_visitor_counter(func):
    def _fn(request, *args, **kwargs):
        response = func(request, *args, **kwargs)

        if 'seen' not in request.COOKIES:
            response.set_cookie('seen', 1)
            survey_code = kwargs.get('survey_code')
            code = kwargs.get('code')

            if survey_code and code:
                SurveyAnswer.objects.filter(
                    survey__is_active=True,
                    survey__code=survey_code,
                    code=code,
                ).update(visitor_counter=F('visitor_counter') + 1)

        return response
    return _fn


def home(request, code):
    survey = get_object_or_404(
        Survey.objects.filter(is_active=True),
        code=code)
    return redirect(survey.answers.create())


@increment_visitor_counter
def survey(request, survey_code, code, page=1):
    answer = get_object_or_404(
        SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    answer.update_status(answer.STARTED)

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
                answer.update_status(answer.FINISHED)

                return redirect(
                    'survey_survey_end',
                    survey_code=survey_code,
                    code=code)
            elif 'prev' in request.POST:
                offset = -1
            else:
                offset = 1

            if 0 < page + offset <= len(pages):
                return redirect(
                    'survey_survey_page',
                    survey_code=survey_code,
                    code=code,
                    page=page + offset)

    else:
        form = QuestionForm(**kwargs)

    return render(request, 'survey/form.html', {
        'survey': answer.survey,
        'answer': answer,
        'form': form,

        'page': page,
        'page_count': len(pages),
        'is_first_page': page == 1,
        'is_last_page': page == len(pages),
    })


@increment_visitor_counter
def survey_end(request, survey_code, code):
    answer = get_object_or_404(
        SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    if request.method == 'POST':
        form = SurveyEndForm(request.POST, instance=answer, label_suffix='')

        if form.is_valid():
            form.save()

            answer.update_status(answer.COMPLETED)

            return redirect(
                'survey_survey_thanks',
                survey_code=survey_code,
                code=code)
    else:
        form = SurveyEndForm(instance=answer, label_suffix='')

    return render(request, 'survey/end.html', {
        'survey': answer.survey,
        'answer': answer,
        'form': form,
    })


def survey_thanks(request, survey_code, code):
    answer = get_object_or_404(
        SurveyAnswer.objects.select_related('survey'),
        survey__is_active=True,
        survey__code=survey_code,
        code=code)

    return render(request, 'survey/thanks.html', {
        'survey': answer.survey,
        'answer': answer,
    })


@staff_member_required
def survey_export(request, code):
    survey = get_object_or_404(Survey, code=code)
    w = xlwt.Workbook()
    ws = w.add_sheet('survey')
    row = 0

    ws.write(row, 0, unicode(survey))
    row += 2

    for col, field in enumerate(SurveyAnswer._meta.fields):
        ws.write(row, col, unicode(field.verbose_name))

    group = None
    col = len(SurveyAnswer._meta.fields) + 1
    question_column = {}

    for question in Question.objects.filter(group__survey=survey).order_by(
            'group', 'ordering').select_related('group'):

        if question.group != group:
            col += 1
            group = question.group
            ws.write(row, col, unicode(group))

        question_column[question.pk] = col
        ws.write(row + 1, col, unicode(question))
        ws.write(row + 2, col, question.get_type_display())
        col += 1
        if question.has_importance:
            ws.write(row + 2, col, _('has importance'))
            col += 1

    row += 3

    for answer in survey.answers.select_related():
        for col, field in enumerate(SurveyAnswer._meta.fields):
            if field.choices:
                ws.write(
                    row, col, getattr(answer, 'get_%s_display' % field.name)())
            else:
                ws.write(row, col, unicode(getattr(answer, field.name)))

        for question, answers in answer.details():
            col = question_column[question.pk]
            ws.write(row, col, unicode(answers['answer']))
            if question.has_importance:
                ws.write(row, col + 1, unicode(answers['importance']))

        row += 1

    output = StringIO.StringIO()
    w.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'inline; filename=survey-%s.xls' % (
        survey.code,
    )
    return response
