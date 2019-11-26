"""" As views gerenciam o que ocorre quando o usuário entra em uma URL do app"""
import requests

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers

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
        return ClippingProject.objects.order_by('-created_date')[0:1000]


def new_project(request):
    """" Cria novo projeto e redireciona para tela de edição. """
    name = str(ClippingProject.objects.count()+1)
    created_date = timezone.now()
    project = ClippingProject(name=name, created_date=created_date)
    project.save()

    # Por enquanto redireciona para o explorador, mas deve já abrir o clipping para edição
    return HttpResponseRedirect(reverse('gerador:explorer'))


def show_rename_project(request, project_id):
    """ Exibe tela de renomear projeto """
    project = ClippingProject.objects.get(id=project_id)

    return render(request, 'gerador/rename_project.html',
                  {'project': project, })


def duplicate_project(request, project_id):
    """" Duplica projeto. """
    project = ClippingProject.objects.get(id=project_id)
    project.pk = None

    project.name = 'Cópia de ' + project.name
    project.created_date = timezone.now()
    project.save()
    return HttpResponseRedirect(reverse('gerador:explorer'))


def rename_project(request, project_id):
    """" Renomeia projeto. """
    project = ClippingProject.objects.get(id=project_id)
    project.name = request.POST.get('new_name')
    project.save()
    return HttpResponseRedirect(reverse('gerador:explorer'))


def archive_project(request, project_id):
    """" Arquiva projeto. """
    project = ClippingProject.objects.get(id=project_id)
    project.is_archived = True
    project.save()
    return HttpResponseRedirect(reverse('gerador:explorer'))


def news_recovery(request, project_id):
    """" Permite recuperar as notícias do banco de dados com parâmetros. """
    project = get_object_or_404(ClippingProject, pk=project_id)

    # api-endpoint
    url = "http://127.0.0.1:8080/noticias"

    # defining a params dict for the parameters to be sent to the API
    params = {'page': 1, 'items': 100}

    # sending get request and saving the response as response object
    api_request = requests.get(url=url, params=params)

    # extracting data in json format
    data = api_request.json()

    # links = data['links']
    data = data['data']
    for data_row in data:
        data_row['is_included'] = project.news_set.filter(
            source_db_id=data_row['id']).count() > 0

    # remover [+N chars]
    for news in data:
        content = news['content']
        if content.find('[+'):
            content = content.split('[+')[0]
            news['content'] = content

    return render(request, 'gerador/news_recovery.html',
                  {'project': project, 'news_result': data, })


def insert_news(request, project_id):
    """" Insere notícia no projeto. """

    project = ClippingProject.objects.get(id=project_id)

    title = request.POST.get('title')
    content = request.POST.get('content')
    author = request.POST.get('author')
    url = request.POST.get('url')
    pub_date = request.POST.get('publishedAt')
    url_to_image = request.POST.get('urlToImage')
    source_db_id = request.POST.get('source_db_id')
    order = project.news_set.all().count()

    project.news_set.create(title=title,
                            content=content,
                            url=url,
                            pub_date=pub_date,
                            author=author,
                            url_to_image=url_to_image,
                            source_db_id=source_db_id,
                            order=order)

    project.save()
    return HttpResponseRedirect(reverse('gerador:news_recovery', args=[project_id]))


def remove_news(request, project_id):
    """" Insere notícia no projeto. """

    project = get_object_or_404(ClippingProject, pk=project_id)

    source_db_id = request.POST.get('source_db_id')

    news_to_remove = project.news_set.filter(
        source_db_id=source_db_id)

    for news in news_to_remove:
        order_of_deleted_news = news.order
        news.delete()
        news_to_reorder = project.news_set.filter(
            order__gt=order_of_deleted_news)
        for other_news in news_to_reorder:
            other_news.order -= 1
            other_news.save()

    return redirect(request.META.get('HTTP_REFERER'))


def clipping_organizer(request, project_id):
    """" Permite ordernar as notícias e inserir cabeçalhos. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    news_set = project.news_set.all()

    return render(request, 'gerador/clipping_organizer.html',
                  {'project': project, 'news_set': news_set})


def news_order_up(request, project_id):
    """ Move uma notícia específica para cima. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    order = request.POST.get('order')

    news_to_up = project.news_set.get(
        order=order)

    order = news_to_up.order

    if news_to_up.order > 0:
        news_above = project.news_set.get(order=order-1)
        news_to_up.order = order-1
        news_above.order = order
        news_above.save()
        news_to_up.save()

    return redirect(request.META.get('HTTP_REFERER'))


def update_header(request, project_id):
    """ Move uma notícia específica para cima. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    order = request.POST.get('order')
    header = request.POST.get('header')

    news_to_update = project.news_set.get(
        order=order)

    news_to_update.header = header
    news_to_update.save()

    return redirect(request.META.get('HTTP_REFERER'))


def download_pdf(request, project_id):
    """ Faz download do clipping como pdf. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    json_str = serializers.serialize("json", project.news_set.all(),
                                     fields=('title', 'content', 'url', 'pub_date',
                                             'author', 'url_to_image', 'header'))
    file_name = 'clipping_' + project.name
    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=' + \
        file_name + '.json'
    return response
