from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {
        'test': 'toto je test',
    }
    return render(request, 'pages/index.html', context)
