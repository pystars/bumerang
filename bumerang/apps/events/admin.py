# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Event
from signals import approve_event


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'created', 'owner_name', 'owner')
    list_filter = ('is_approved', 'opened')
    list_display_links = ('__unicode__',)

    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data and obj.is_approved:
            approve_event.send(self, event=obj)
        obj.save()


admin.site.register(Event, EventAdmin)
