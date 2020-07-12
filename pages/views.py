# -*- coding: utf-8 -*-
from django.shortcuts import render
from forms.forms import UserForm


def index(request):
    submitbutton = request.POST.get("submit")

    bookname = ''
    authorname = ''


    form = UserForm(request.POST or None)
    if form.is_valid():
        bookname = form.cleaned_data.get("book_name")


    context = {'form': form, 'bookname': bookname, 'authorname': authorname,
               'submitbutton': submitbutton}

    return render(request, 'pages/index.html', context)
