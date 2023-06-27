from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse



# Create your views here.


def index(request):
    return render(request,'pages/home/ms1/index.html')


def layout2(request):
    return render(request, 'pages/home/ms2/layout-2.html')

def layout3(request):
    return render(request, 'pages/home/ms3/layout-3.html')
