# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.advices.models import *

class AdviceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Advice, AdviceAdmin)