""" Site de Admin """
from django.contrib import admin
from .models import ClippingProject, News

admin.site.register(ClippingProject)
admin.site.register(News)
