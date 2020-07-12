from django import forms


class UserForm(forms.Form):
    book_name = forms.CharField(max_length=100)
    author_name = forms.CharField(max_length=100)

