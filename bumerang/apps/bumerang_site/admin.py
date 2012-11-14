# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld
from tinymce.widgets import TinyMCE


class CustomFlatpageForm(FlatpageForm):
    class Meta(FlatpageForm.Meta):
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }

    def __init__(self, *args, **kwargs):
        super(CustomFlatpageForm, self).__init__(*args, **kwargs)
        self.fields['template_name'].initial = 'flatpages/about.html'
        self.fields['sites'].initial = [i[0]
                                        for i in self.fields['sites'].choices]


class FlatPageAdmin(FlatPageAdminOld):
    form = CustomFlatpageForm
    change_form_template = 'flatpages/admin/change_form.html'


# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)