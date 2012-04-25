# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Profile


class ProfileAdmin(admin.ModelAdmin):
    exclude = ['first_name', 'last_name', 'email']
    prepopulated_fields = {'info_email': ['username'],}

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


admin.site.register(Profile, ProfileAdmin)
