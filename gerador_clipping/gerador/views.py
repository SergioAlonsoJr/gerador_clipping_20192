"""" As views gerenciam o que ocorre quando o usuário entra em uma URL do app"""
import json
import requests

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.utils import timezone
from django.urls import reverse
from django.views import generic
from .models import ClippingProject, News


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


def news_recovery(request, project_id, page=1, *args):
    """" Permite recuperar as notícias do banco de dados com parâmetros. """
    project = get_object_or_404(ClippingProject, pk=project_id)

    # api-endpoint
    url = "http://127.0.0.1:8080/noticias"

    # defining a params dict for the parameters to be sent to the API
    params = {'page': 1, 'items': 100}

    # sending get request and saving the response as response object
    r = requests.get(url=url, params=params)

    # extracting data in json format
    data = r.json()

    links = data['links']
    data = data['data']

    # remover [+N chars]
    for news in data:
        content = news['content']
        if content.find('[+'):
            content = content.split('[+')[0]
            news['content'] = content

    return render(request, 'gerador/news_recovery.html',
                  {'project': project, 'news_result': data, 'links': links})


def insert_news(request, project_id):
    """" Insere notícia no projeto. """
    news_data = request.POST.get('news_data')
    
    print(news_data)
    news_data = json.loads(news_data)
    project = ClippingProject.objects.get(id=project_id)
    print(type(news_data))
    title = news_data['title']
    content = news_data['content']
    url = news_data['url']
    pub_date = news_data['publishedAt']
    author = news_data['author']
    url_to_image = news_data['urlToImage']
    source_db_id = news_data['id']
    news = News(title=title, content=content, url=url, pub_date=pub_date,
                author=author, url_to_image=url_to_image, source_db_id=source_db_id)
    news.save()
    return HttpResponseRedirect(reverse('gerador:news_recovery'))


def clipping_organizer(request, project_id):
    """" Permite ordernar as notícias e inserir cabeçalhos. """
    response = "Este é o organizador do projeto %s."
    return HttpResponse(response % project_id)
