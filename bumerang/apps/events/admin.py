# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Event, Juror, GeneralRule, NewsPost, Nomination, Participant,
    ParticipantVideo, VideoNomination)
from .signals import approve_event, winners_public, participant_reviewed


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
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if getattr(request, '_obj', None):
            if db_field.name == 'video':
                kwargs['queryset'] = request._obj.owner.video_set
            elif db_field.name == 'nomination':
                kwargs['queryset'] = request._obj.event.nomination_set
        return super(
            ParticipantVideoAdminInline, self).formfield_for_foreignkey(
            db_field, request=request, **kwargs)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    readonly_fields = ['index_number']
    inlines = [ParticipantVideoAdminInline]

    def get_object(self, request, object_id):
        # we save participant to request for providing it in inlines
        obj = super(ParticipantAdmin, self).get_object(request, object_id)
        if obj is not None:
            request._obj = obj
        return obj

    def response_change(self, request, new_object):
        response = super(
            ParticipantAdmin, self).response_change(request, new_object)
        if new_object.is_accepted and new_object.participant_videos.exists():
            participant_reviewed.send(self.__class__, participant=new_object)
        return response


class VideoNominationInline(admin.TabularInline):
    model = VideoNomination
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'participant_video' and getattr(
                request, '_obj', None):
            kwargs['queryset'] = request._obj.user_selected_participantvideo_set
        return super(VideoNominationInline, self).formfield_for_foreignkey(
            db_field, request=request, **kwargs)


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
