"""" Para onde cada URL deve direcionar o usuário. """
from django.urls import path
from . import views

app_name = 'gerador'
urlpatterns = [
    path('', views.ExplorerView.as_view(), name='explorer'),
    path('<int:project_id>/show_rename/',
         views.show_rename_project, name='show_rename_project'),
    path('<int:project_id>/rename/',
         views.rename_project, name='rename_project'),
    path('new_project/', views.new_project, name='new_project'),
    path('<int:project_id>/archive/',
         views.archive_project, name='archive_project'),
    path('<int:project_id>/show_archive/',
         views.show_archive_project, name='show_archive_project'),
    path('<int:project_id>/duplicate/',
         views.duplicate_project, name='duplicate_project'),
    path('<int:project_id>/insert_news/',
         views.insert_news, name='insert_news'),
    path('<int:project_id>/clipping_organizer/',
         views.clipping_organizer, name='clipping_organizer'),
    path('<int:project_id>/remove_news/',
         views.remove_news, name='remove_news'),
    path('<int:project_id>/news_order_up/',
         views.news_order_up, name='news_order_up'),
    path('<int:project_id>/update_header/',
         views.update_header, name='update_header'),
    path('<int:project_id>/download_pdf/',
         views.download_pdf, name='download_pdf'),

    path('<int:project_id>/recovery/', views.news_recovery, name='news_recovery'),
    path('<int:project_id>/organizer/',
         views.clipping_organizer, name='organizer'),
]
