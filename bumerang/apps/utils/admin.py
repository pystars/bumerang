# -*- coding: utf-8 -*-
from django.contrib import admin


class TitleSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "sort_order",)
    list_editable = ("title", "sort_order",)
