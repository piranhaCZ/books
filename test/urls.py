from django.urls import path

from . import views

urlpatterns = [
    # ex: /test/
    path('', views.index, name='index'),
    # ex: /test/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /test/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /test/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]