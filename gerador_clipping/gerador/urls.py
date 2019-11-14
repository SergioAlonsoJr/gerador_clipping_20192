"""" Para onde cada URL deve direcionar o usuário. """
from django.urls import path
from . import views

app_name = 'gerador'
urlpatterns = [
    path('', views.ExplorerView.as_view(), name='explorer'),
    path('new_project/', views.new_project, name='new_project'),
    path('<int:project_id>/archive/',
         views.archive_project, name='archive_project'),
    path('<int:project_id>/recovery/', views.news_recovery, name='news_recovery'),
    path('<int:project_id>/organizer/', views.clipping_organizer, name='organizer'),
]
