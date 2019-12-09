"""" As views gerenciam o que ocorre quando o usuário entra em uma URL do app"""
import datetime
import os
import tempfile
import zipfile
import socket
import requests


from pdf2image import convert_from_path

from pyreportjasper import JasperPy

from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers, files


from django.utils import timezone
from django.urls import reverse
from django.views import generic

from .models import ClippingProject, News, OrganizationIdentity


class ExplorerView(generic.ListView):
    """" Permite gerenciar projetos de clipping. """

    if OrganizationIdentity.objects.count() == 0:
        new_organization_identity = OrganizationIdentity()
        new_organization_identity.save()

    template_name = 'gerador/explorer.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """ Retornar os 1000 projetos mais recentes. """
        return ClippingProject.objects.order_by('-created_date')[0:1000]


def new_project(request):
    """" Cria novo projeto e redireciona para tela de edição. """
    name = request.POST.get('clipping_name', str(
        ClippingProject.objects.count()+1))
    created_date = timezone.now()
    project = ClippingProject(name=name, created_date=created_date)
    project.save()

    # Por enquanto redireciona para o explorador, mas deve já abrir o clipping para edição
    return HttpResponseRedirect(reverse('gerador:explorer'))


def show_rename_project(request, project_id):
    """ Exibe tela de renomear projeto """
    project = ClippingProject.objects.get(id=project_id)

    return render(request, 'gerador/rename_project.html',
                  {'project': project})


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


def news_recovery(request, project_id):
    """" Permite recuperar as notícias do banco de dados com parâmetros. """
    project = get_object_or_404(ClippingProject, pk=project_id)
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    ip_split = ip_addr.split('.')
    try:
        params = {'page': request.GET.get('page', 1), 'items': 5000}
        is_connected = False

        address_to_try = request.session.get('bd_address', 0)
        while not is_connected:
            url = 'http://'+ip_split[0] + '.' + ip_split[1] + \
                '.' + ip_split[2] + '.' + \
                str(address_to_try) + ":8080/noticias"
            try:
                api_request = requests.get(url=url, params=params)
            except requests.exceptions.RequestException:
                request.session['bd_address'] = 1

                address_to_try += 1
                if address_to_try == 7:  # Excedeu o limite de tentativas
                    raise requests.exceptions.RequestException

            else:
                request.session['bd_address'] = address_to_try
                is_connected = True

        raw_data = api_request.json()

        news_list = raw_data['data']

        search_age = int(request.GET.get('age', request.session.get('age', 7)))
        request.session['age'] = search_age

        # Filtro por Idade
        for i in range(len(news_list) - 1, -1, -1):
            found_term = False
            # formatar tempo para humanos e para django
            date_time_str = news_list[i]['publishedAt']

            date_time_obj = datetime.datetime.strptime(
                date_time_str, '%Y-%m-%dT%H:%M:%SZ')

            date_difference = datetime.datetime.now(
                date_time_obj.tzinfo) - date_time_obj

            if date_difference.days > search_age:
                del news_list[i]
                continue

            news_list[i]['publishedAt_human'] = date_time_obj
            news_list[i]['age_minutes'] = date_difference.days * \
                60*24 + date_difference.seconds/60

        search_term_packed = request.GET.get(
            'search_term', request.session.get('search_term', ''))
        request.session['search_term'] = search_term_packed
        search_terms = search_term_packed.split()

        # Filtro por search_term
        if len(search_terms) > 0:
            for i in range(len(news_list) - 1, -1, -1):
                found_term = False
                for search_term in search_terms:
                    if search_term in news_list[i]['title'] or \
                            search_term in news_list[i]['content']:
                        found_term = True
                        break

                if found_term:
                    continue

                del news_list[i]

        # Ordena por score ou published_at
        sort = request.GET.get('sort', request.session.get('sort', 'score'))
        request.session['sort'] = sort

        if sort == 'score':
            news_list = sorted(news_list, key=lambda k: k['score'])
        else:
            news_list = sorted(news_list, key=lambda k: k['age_minutes'])

        # configura detalhes nas notícias filtradas
        for news in news_list:

            # Marca notícias que já foram inclusas
            news['is_included'] = project.news_set.filter(
                source_db_id=news['id']).count() > 0

            # remover [+N chars]
            content = news['content']
            if content.find('[+'):
                content = content.split('[+')[0]
                news['content'] = content

            # Curar tamanho da string
            paragraphs = content.split('\n')
            curated_content = ''
            while len(curated_content) < len(content)/2:
                curated_content = paragraphs.pop(0)

            curated_content = curated_content.rstrip() + ' '

            news['content'] = curated_content

        return render(request, 'gerador/news_recovery.html',
                      {'project': project, 'news_result': news_list,
                       'search_terms': search_term_packed,
                       'age': search_age,
                       'sort': sort})

    except requests.exceptions.RequestException:

        return HttpResponse("Erro ao conectar ao Banco de Dados HealthNewsAPI."
                            " Verifique se o serviço está executando e se há internet.")


def insert_news(request, project_id):
    """" Insere notícia no projeto. """

    project = ClippingProject.objects.get(id=project_id)
    current_identity = OrganizationIdentity.objects.all()[0]
    title = request.POST.get('title')
    content = request.POST.get('content')

    author = request.POST.get('author')
    url = request.POST.get('url')
    pub_date = request.POST.get('publishedAt')
    url_to_image = request.POST.get('urlToImage')
    source_db_id = request.POST.get('source_db_id')
    human_pub_date = request.POST.get('human_pub_date')
    order = project.news_set.all().count()

    created_news = News(project=project,
                        title=title,
                        content=content,
                        url=url,
                        pub_date=pub_date,
                        author=author,
                        url_to_image=url_to_image,
                        source_db_id=source_db_id,
                        order=order,
                        human_pub_date=human_pub_date,
                        clipping_creator=current_identity.clipping_creator)

    # Primeiro verifica se já temos uma imagem similar salva
    file_name = url_to_image[8:]

    try:
        request = requests.get(url_to_image, stream=True)
    except requests.exceptions.RequestException:
        return HttpResponse("Erro ao baixar imagem da notícia."
                            " Verifique se há internet.")

    if request.status_code != 200:
        raise BaseException("Erro ao carregar imagem: " +
                            request.status_code + url_to_image)

    temporary_file = tempfile.NamedTemporaryFile()
    for block in request.iter_content(1024 * 8):
        if not block:
            break

        temporary_file.write(block)

    created_news.image.save(file_name, files.File(temporary_file))
    created_news.save()
    created_news.crop_image()
    return HttpResponseRedirect(reverse('gerador:news_recovery', args=[project_id]))


def remove_news(request, project_id):
    """" Insere notícia no projeto. """

    project = get_object_or_404(ClippingProject, pk=project_id)

    source_db_id = request.POST.get('source_db_id')

    news_to_remove = project.news_set.filter(
        source_db_id=source_db_id)

    for news in news_to_remove:
        order_of_deleted_news = news.order
        news.image.delete()
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


def update_image_news(request, project_id):
    """ Substitui a imagem de uma notícia. """
    if request.method == 'POST' and request.FILES.get('new_image', False):
        project = get_object_or_404(ClippingProject, pk=project_id)
        order = request.POST.get('order')

        news_selected = project.news_set.get(
            order=order)

        new_image = request.FILES['new_image']

        news_selected.image.delete()
        news_selected.image.save(new_image.name, files.File(new_image))
        news_selected.source_db_id = "0"
        news_selected.url_to_image = news_selected.image.url

        news_selected.save()

        news_selected.crop_image()

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
                                         'author', 'image', 'header', 'human_pub_date',
                                         'clipping_creator'),
                                 stream=xml_file)

    input_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..')) + "/clipping_A4_xml.jrxml"

    clean_name = ''.join(e for e in project.name if e.isalnum())
    pdf_file_location = data_folder + '/clipping_' + \
        str(project.id) + '_' + clean_name

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

    return FileResponse(open(pdf_file_location, 'rb'), content_type='application/pdf',
                        as_attachment=True)


def download_jpeg(request, project_id):
    """ Faz download do clipping como jpeg. Incompleto """

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

    input_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..')) + "/clipping_TV_xml.jrxml"
    pdf_file_location = data_folder + '/clipping_TV_' + project.name

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
        locale='pt_BR'
    )
    pdf_file = pdf_file_location + '.pdf'

    pages = convert_from_path('pdf_file_location', 500)
    for index, page in enumerate(pages):
        page.save(pdf_file+'/'+index+'_out.jpg', 'JPEG')

    zipf = zipfile.ZipFile(
        data_folder + '/clipping_tv.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, _, pages in os.walk(pdf_file_location+'/'):
        for file in pages:
            zipf.write(os.path.join(root, file))

    zipf.close()

    return redirect(request.META.get('HTTP_REFERER'))


def show_organization_identity(request, project_id):
    """ Mostra a identidade da organização: os criadores de clipping """
    current_identity = OrganizationIdentity.objects.all()[0]
    project = get_object_or_404(ClippingProject, pk=project_id)
    return render(request, 'gerador/organization_identity.html',
                  {'project': project, 'identity': current_identity})


def update_organization_identity(request, project_id):
    """ Atualiza a identidade dos criadores de clipping """
    current_identity = OrganizationIdentity.objects.all()[0]
    current_identity.clipping_creator = request.POST.get('clipping_creator')
    current_identity.save()
    # Atualiza em todas as notícias do projeto atual

    project = get_object_or_404(ClippingProject, pk=project_id)

    news_set = project.news_set.all()
    for news in news_set:
        news.clipping_creator = current_identity.clipping_creator
        news.save()

    return render(request, 'gerador/clipping_organizer.html',
                  {'project': project, 'news_set': news_set})
