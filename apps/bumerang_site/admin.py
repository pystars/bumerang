# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld

class FlatPageAdmin(FlatPageAdminOld):
    class Media:
        js = [
            'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            'j/tinymce_setup.js',
        ]

# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)