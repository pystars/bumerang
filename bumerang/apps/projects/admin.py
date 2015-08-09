# -*- coding: utf-8 -*-
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import Project


# class ProjectAdmin(admin.ModelAdmin):

admin.site.register(Project)
