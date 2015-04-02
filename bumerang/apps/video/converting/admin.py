# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import EncodeJob


class EncodeJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', '__unicode__', 'get_state_display', 'created_at',
                    'last_modified', 'lead_time']
    list_display_links = ['job_id', '__unicode__']

admin.site.register(EncodeJob, EncodeJobAdmin)
