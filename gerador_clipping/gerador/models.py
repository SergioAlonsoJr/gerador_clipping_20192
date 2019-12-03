#!-*- conding: utf8 -*-
"""" Os modelos dos dados do aplicativo. """
from django.db import models\

from django_resized import ResizedImageField


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
    human_pub_date = models.CharField(max_length=500, default='0')
    author = models.CharField(max_length=500, default='0')
    url_to_image = models.CharField(max_length=500, default='0')
    image = models.ImageField(
        upload_to='gerador/jasper/images', blank=True, max_length=1000)
    source_db_id = models.CharField(max_length=500, default='0')
    header = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]

    """ 
    def crop_image(self):
        

        img = Image.open(self.image.path)
        # Size of the image in pixels (size of orginal image)
        # (This is not mandatory)
        width, height = img.size
        left = 0
        top = 0
        right = width
        bottom = height
        if width >= height * 16/9:
            # imagem muito horizontal, recorta esquerda e direita
            new_width = int(height/(16/9))
            left = int(new_width-width)/2
            right = new_width-left
        else:
            # imagem muito vertical, recorta cima e baixo
            new_height = int(width*(16/9))
            top = int(new_height-height)/2
            bottom = new_height-top

        cropped_image = img.crop(
            (left, top, right, bottom))
        self.image.save(self.image.name, cropped_image)

        self.save()
    """
