# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Profile

class ProfileAdmin(admin.ModelAdmin):
    exclude = ['first_name', 'last_name', 'email']
    prepopulated_fields = {'info_email': ['username'],}


admin.site.register(Profile, ProfileAdmin)
