# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld


class FlatPageAdmin(FlatPageAdminOld):
    change_form_template = 'flatpages/admin/change_form.html'


# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)