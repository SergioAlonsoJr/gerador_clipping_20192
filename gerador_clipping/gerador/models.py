#!-*- conding: utf8 -*-
"""" Os modelos dos dados do aplicativo. """
from django.db import models

# Create your models here.


class ClippingProject(models.Model):
    """" O projeto do clipping em produção. Possui nome, data e conteúdo. """
    name = models.CharField(max_length=100)

    created_date = models.DateTimeField('date created')
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Content(models.Model):
    """" Conteúdo pode ser Notícia (News) ou Cabeçalho (Header). Contém índice."""
    project = models.ForeignKey(ClippingProject, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return "{} {}".format("Content", self.index)


class News(Content):
    """" News é uma notícia do clipping. """
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    url = models.CharField(max_length=300)
    pub_date = models.DateTimeField('published date')
    author = models.CharField(max_length=100, default='0')
    url_to_image = models.CharField(max_length=100, default='0')
    source_db_id = models.CharField(max_length=300, default='0')

    def __str__(self):
        return "{} {}".format("News", self.title)
