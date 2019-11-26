#!-*- conding: utf8 -*-
"""" Os modelos dos dados do aplicativo. """
from django.db import models\



class ClippingProject(models.Model):
    """" O projeto do clipping em produção. Possui nome, data e conteúdo. """
    name = models.CharField(max_length=100)

    created_date = models.DateTimeField('date created')
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class News(models.Model):
    """" News é uma notícia do clipping. """
    project = models.ForeignKey(ClippingProject, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=500)
    content = models.CharField(max_length=500)
    url = models.CharField(max_length=500)
    pub_date = models.DateTimeField('published date')
    author = models.CharField(max_length=500, default='0')
    url_to_image = models.CharField(max_length=500, default='0')
    source_db_id = models.CharField(max_length=500, default='0')
    header = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
