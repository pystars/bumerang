# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Event, Juror, GeneralRule, NewsPost, Nomination, Participant,
    ParticipantVideo, VideoNomination)
from .signals import approve_event, winners_public


class JurorInlineAdmin(admin.StackedInline):
    model = Juror
    fields = ['email', 'info_second_name', 'info_name', 'info_middle_name',
              'description', 'min_avatar']
    extra = 0


class GeneralRuleInlineAdmin(admin.TabularInline):
    model = GeneralRule
    extra = 0


class NewsPostInlineAdmin(admin.TabularInline):
    model = NewsPost
    extra = 0


class NominationInlineAdmin(admin.TabularInline):
    model = Nomination
    extra = 0


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'created', 'owner_name', 'owner')
    list_filter = ('is_approved', 'opened')
    list_display_links = ('__unicode__',)
    inlines = [
        NominationInlineAdmin,
        JurorInlineAdmin,
        GeneralRuleInlineAdmin,
        NewsPostInlineAdmin
    ]

    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data and obj.is_approved:
            approve_event.send(self, event=obj)
        if 'publish_winners' in form.changed_data and obj.publish_winners:
            winners_public.send(self, event=obj)
        obj.save()


class ParticipantVideoAdminInline(admin.TabularInline):
    model = ParticipantVideo
    extra = 0
    readonly_fields = ['video']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(
            ParticipantVideoAdminInline, self).formfield_for_foreignkey(
            db_field, request=None, **kwargs)
        if db_field.name == 'nomination':
            formfield.queryset = request._obj.event.nomination_set
        return formfield

    def has_add_permission(self, request):
        return False


class ParticipantAdmin(admin.ModelAdmin):
    list_display = []
    readonly_fields = ['owner', 'event', 'index_number']
    inlines = [ParticipantVideoAdminInline]

    def get_object(self, request, object_id):
        # we save participant to request for providing it in inlines
        obj = super(ParticipantAdmin, self).get_object(request, object_id)
        request._obj = obj
        return obj


class VideoNominationInline(admin.TabularInline):
    model = VideoNomination
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(VideoNominationInline, self).formfield_for_foreignkey(
            db_field, request=None, **kwargs)
        if db_field.name == 'participant_video':
            formfield.queryset = request._obj.user_selected_participantvideo_set
        return formfield


class NominationAdmin(admin.ModelAdmin):
    list_display = []
    fields = ['title', 'event']
    readonly_fields = ['event', 'title']
    inlines = [VideoNominationInline]

    def get_object(self, request, object_id):
        # we save nomination to request for providing it in inlines
        obj = super(NominationAdmin, self).get_object(request, object_id)
        request._obj = obj
        return obj


admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Nomination, NominationAdmin)
