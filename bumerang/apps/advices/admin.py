# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from bumerang.apps.advices.models import Advice


class AdviceAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    change_form_template = 'advices/admin/change_form.html'


admin.site.register(Advice, AdviceAdmin)
