""" Site de Admin """
from django.contrib import admin
from .models import ClippingProject, News, OrganizationIdentity

admin.site.register(ClippingProject)
admin.site.register(News)
admin.site.register(OrganizationIdentity)
