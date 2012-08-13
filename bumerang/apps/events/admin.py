# -*- coding: utf-8 -*-
from django.contrib import admin

from bumerang.apps.events.models import Event


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('owner',)
    list_display = ('id', '__unicode__', 'created', 'owner_name', 'owner')
    list_filter = ('is_approved', 'opened')
    list_display_links = ('__unicode__',)


admin.site.register(Event, EventAdmin)
