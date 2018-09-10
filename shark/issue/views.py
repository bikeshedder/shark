from django.template.response import TemplateResponse


def issue_create(request):
    return TemplateResponse(request, 'issue/issue_create.html', {
    })
