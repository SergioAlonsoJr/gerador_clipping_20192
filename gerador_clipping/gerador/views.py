"""" As views gerenciam o que ocorre quando o usuário entra em uma URL do app"""
import json
import requests

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.utils import timezone
from django.urls import reverse
from django.views import generic
from .models import ClippingProject


class ExplorerView(generic.ListView):
    """" Permite gerenciar projetos de clipping. """
    template_name = 'gerador/explorer.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """ Retornar os 100 projetos mais recentes. """
        return ClippingProject.objects.order_by('-created_date')[:100]


def new_project(request):
    """" Cria novo projeto e redireciona para tela de edição. """
    name = str(ClippingProject.objects.count()+1)
    created_date = timezone.now()
    project = ClippingProject(name=name, created_date=created_date)
    project.save()

    # Por enquanto redireciona para o explorador, mas deve já abrir o clipping para edição
    return HttpResponseRedirect(reverse('gerador:explorer'))


def archive_project(request, project_id):
    """" Arquiva projeto. """
    project = ClippingProject.objects.get(id=project_id)
    project.is_archived = True
    project.save()
    return HttpResponseRedirect(reverse('gerador:explorer'))


def news_recovery(request, project_id, *args):
    """" Permite recuperar as notícias do banco de dados com parâmetros. """
    project = get_object_or_404(ClippingProject, pk=project_id)

    url = 'http://127.0.0.1:8080/noticias'
    payload = {}
    headers = {'content-type': 'application/json'}

    response = requests.get(url, data=json.dumps(payload), headers=headers)

    return render(request, 'gerador/news_recovery.html',
                  {'project': project, 'news_result': response.json})

# def get_news(request,project_id, *args):
#     r = requests.get('http://127.0.0.1:8080/noticias')
#     project = get_object_or_404(ClippingProject, pk=project_id)
#     return render(request, 'gerador/news_recovery.html', {'project': project})
#     """ Retorna do banco de dados as notícias com os parâmetros."""


def clipping_organizer(request, project_id):
    """" Permite ordernar as notícias e inserir cabeçalhos. """
    response = "Este é o organizador do projeto %s."
    return HttpResponse(response % project_id)
