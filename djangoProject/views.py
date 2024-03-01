from django.http import HttpResponse


def hello(request):
    return HttpResponse('hello')


def index(request):
    return HttpResponse('hhhh')