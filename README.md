# Gerador de Clippings 2019.2 
Gerador de Clippings da Disciplina Sistemas de Informação 2019.2

# Como instalar projeto

* A aplicação vai estar no localhost:8000
* O banco de dados da [HealthNewsAPI](https://github.com/healthnewsapi/HealthNewsAPI) precisa estar executando.

## Imagem para desenvolvedor
Esse caminho facilita modificar o código e ver a alteração em tempo real (hot reload)
1. Clone ou Fork este repositório
1. Esteja no mesmo diretório que o docker-compose.yml
1. `docker-compose build  # use sudo para ter o privilégio`
1. `docker-compose up`

## Imagem para usuário

* Execute o docker com a imagem:
`docker run sergioalonsojr/gerador_clipping # use sudo para ter o privilégio`

# Como herdar este projeto

O código do projeto envolve três partes: Regras de Negócio, Interface e Layout do Clipping.

## 1) Regras de Negócio

É onde são implementadas como as coisas funcionam e como os dados não-visíveis pelo usuário são transformados: modelos, bancos de dados, filtro e ordenamento da recuperação das notícias, esqueleto das páginas e dockerização. Essa parte fornece os dados para a interface, recebe as modificações feitas pelo usuário, e cria o XML que o Layout do Clipping utiliza.
Para cuidar dessa parte é necessário dominar:
 - [Python 3](https://www.codecademy.com/learn/learn-python-3)
 - [HTML](https://www.codecademy.com/learn/learn-html)
 - [Django](https://www.djangoproject.com/) (O tutorial também explica sobre a organização das pastas do projeto)
 - [Docker](https://www.docker.com/)
 
 ## 2) Interface
 
 É onde são implementadas coisas como a estruturação, estética e dinâmica das páginas. Recebe informações das regras de negócio e devolve os inputs do usuário.
 Para cuidar dessa parte é necessário dominar:
 - [HTML](https://www.codecademy.com/learn/learn-html)
 - [CSS](https://www.codecademy.com/learn/learn-css)
 - [Javascript](https://www.codecademy.com/learn/introduction-to-javascript)
 
 ## 3) Layout do Clipping
 
 É onde é montado o layout do clipping, que recebe das regras de nogício os dados por arquivos XML e produz o PDF.
 Para cuidar dessa parte é necessário dominar:
  - [JasperSoft Studio](https://community.jaspersoft.com/system/files/restricted-docs/jaspersoft-studio-user-guide_7.pdf)

# Coisas para melhorar no artefato em atualizações futuras

 - Interface mais dinâmica com [Vue](https://vuejs.org/) e [Axios](https://br.vuejs.org/v2/cookbook/using-axios-to-consume-apis.html); e multithreading com [Celery](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html)
 - Clipping formato para a televisão do corredor da FS. Pode ser feito [convertendo um PDF em JPEG](https://stackoverflow.com/questions/46184239/extract-a-page-from-a-pdf-as-a-jpeg)
 - Opção do usuário atualizar título e corpo da notícia
 - Opção do usuário atualizar identidade visual substituindo o plano de fundo, e as logomarcas
 - Opção do usuário upar seu próprio template do JasperSoft Studio
 - Escrever casos de [teste automatizados](https://docs.djangoproject.com/en/2.2/intro/tutorial05/) para melhorar qualidade técnica do código
 - Instalar Jaspersoft em seu próprio [container Docker](https://community.jaspersoft.com/project/jaspersoft-docker) para permitir uma solução mais robusta
 - A recuperação das notícias com filtro e ordenamento seria mais agil e mais robusta se fosse feita dentro da [API do Banco de Dados](https://github.com/healthnewsapi/HealthNewsAPI)
 - Opção do sistema indicar ao usuário quais notícias já foram inseridas em outros clippings
 - Criar [tooltips](https://www.w3schools.com/howto/howto_css_tooltip.asp) que ajudam o usuário a usar o sistema e talvez uma página manual sobre como usar o sistema
 - Para mais ideias, consultar chefes da Sala de Situação
 
 # [Link para relatório](https://pt.overleaf.com/read/zrybfcvxpfmx)
 
 
