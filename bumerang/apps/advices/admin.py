# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTAdminForm
from feincms.admin.tree_editor import TreeEditor
from tinymce.widgets import TinyMCE

from bumerang.apps.advices.models import Advice


class AdviceForm(MPTTAdminForm):
    class Meta:
        model = Advice
        exclude = ('sort_order',)
        widgets = {
            'description': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }


class AdviceAdmin(TreeEditor):
    form = AdviceForm
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Advice, AdviceAdmin)
