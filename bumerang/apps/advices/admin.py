# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from bumerang.apps.advices.models import Advice


class AdviceAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    class Media:
        js = [
            'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            'j/tinymce_setup.js',
        ]


admin.site.register(Advice, AdviceAdmin)