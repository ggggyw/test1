from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, '首页.html')
