"""" As views gerenciam o que ocorre quando o usuário entra em uma URL do app"""
import datetime
import os
import tempfile
import requests

from pyreportjasper import JasperPy

from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers, files

from django.utils import timezone
from django.urls import reverse
from django.views import generic

from .models import ClippingProject, News


class ExplorerView(generic.ListView):
    """" Permite gerenciar projetos de clipping. """
    template_name = 'gerador/explorer.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """ Retornar os 1000 projetos mais recentes. """
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


def show_archive_project(request, project_id):
    """" Tela para confirmar arquivamento do projeto. """
    project = ClippingProject.objects.get(id=project_id)

    return render(request, 'gerador/delete_confirmation.html',
                  {'project': project, })


def archive_project(request, project_id):
    """" Arquiva projeto. """
    project = ClippingProject.objects.get(id=project_id)
    project.is_archived = True
    project.save()
    return HttpResponseRedirect(reverse('gerador:explorer'))


BD_ADDRESS = 1


def news_recovery(request, project_id):
    """" Permite recuperar as notícias do banco de dados com parâmetros. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    # print(os.system("java -version"))
    try:
        params = {'page': 1, 'items': 1000}
        is_connected = False
        global BD_ADDRESS
        address_to_try = BD_ADDRESS
        while not is_connected:
            url = "http://172.18.0." + str(address_to_try) + ":8080/noticias"
            try:
                api_request = requests.get(url=url, params=params)
            except requests.exceptions.RequestException:
                if BD_ADDRESS != 1:
                    BD_ADDRESS = 1

                address_to_try += 1
                if address_to_try == 7:  # Excedeu o limite de tentativas
                    raise requests.exceptions.RequestException

            else:
                BD_ADDRESS = address_to_try
                is_connected = True

        # extracting data in json format
        data = api_request.json()

        # links = data['links']
        data = data['data']
        for data_row in data:
            data_row['is_included'] = project.news_set.filter(
                source_db_id=data_row['id']).count() > 0

        for news in data:
            # remover [+N chars]
            content = news['content']
            if content.find('[+'):
                content = content.split('[+')[0]
                news['content'] = content

            # formatar tempo para humanos e para django
            date_time_str = news['publishedAt']

            date_time_obj = datetime.datetime.strptime(
                date_time_str, '%Y-%m-%dT%H:%M:%SZ')

            news['publishedAt_human'] = date_time_obj

        return render(request, 'gerador/news_recovery.html',
                      {'project': project, 'news_result': data, })

    except requests.exceptions.RequestException:

        return HttpResponse("Erro ao conectar ao Banco de Dados HealthNewsAPI."
                            " Verifique se o serviço está executando e se há internet.")


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

    # Primeiro verifica se já temos uma imagem similar salva
    file_name = url_to_image[8:]
    data_folder = os.path.dirname(os.path.abspath(
        __file__)) + "static/gerador/jasper"
    local_file_name = data_folder + '/static/gerador/jasper/images/' + file_name
    if os.path.exists(local_file_name):
        print("Local File Exists")
        temporary_file = open(local_file_name, "r")
    else:
        print(url_to_image)
        try:
            request = requests.get(url_to_image, stream=True)
        except requests.exceptions.RequestException:
            return HttpResponse("Erro ao baixar imagem da notícia."
                                " Verifique se há internet.")

        if request.status_code != 200:
            print(url_to_image)
            print(request.status_code)
            raise BaseException("Erro ao carregar imagem")
            # Nope, error handling, skip file etc etc etc

        temporary_file = tempfile.NamedTemporaryFile()
        for block in request.iter_content(1024 * 8):

            if not block:
                break

            temporary_file.write(block)

    created_news = News(project=project,
                        title=title,
                        content=content,
                        url=url,
                        pub_date=pub_date,
                        author=author,
                        url_to_image=url_to_image,
                        source_db_id=source_db_id,
                        order=order)

    created_news.image.save(file_name, files.File(temporary_file))
    created_news.save()
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

    data_folder = os.path.dirname(os.path.abspath(
        __file__)) + "/static/gerador/jasper"

    data_file = data_folder + '/data.xml'

    with open(data_file, 'w') as xml_file:
        xmlserializer = serializers.get_serializer("xml")
        xml_serializer = xmlserializer()
        xml_serializer.serialize(project.news_set.all(),
                                 fields=('title', 'content', 'url', 'pub_date',
                                         'author', 'image', 'header'),
                                 stream=xml_file)

    #

    input_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..')) + "/clipping_A4_xml.jrxml"
    print(input_file)
    pdf_file_location = data_folder + '/clipping_' + project.name

    jasper = JasperPy()

    jasper.process(
        input_file,
        output_file=pdf_file_location,
        format_list=["pdf"],
        parameters={},
        db_connection={
            'data_file': data_file,
            'driver': 'xml',
            'xml_xpath': 'django-objects/object',
        },
        locale='pt_BR'  # LOCALE Ex.:(en_US, de_GE)
    )
    pdf_file_location = pdf_file_location + '.pdf'
    print('Result is the file below.')
    # print()

    return FileResponse(open(pdf_file_location, 'rb'), content_type='application/pdf', as_attachment=True)

    # return redirect(request.META.get('HTTP_REFERER'))
