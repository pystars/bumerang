# -*- coding: utf-8 -*-
from django import forms

from bumerang.apps.events.models import (Event, FestivalGroup, Nomination,
    Participant, ParticipantVideo)
from bumerang.apps.utils.forms import (S3StorageFormMixin, TemplatedForm,
    EditFormsMixin)


#class FestivalProfileSettingsForm(EditFormsMixin, TemplatedForm):
#    text_rules = forms.CharField(label=u'Правила фестиваля', widget=Textarea)
#
#    class Meta:
#        model = Festival
#        fields = (
#            'opened',
#            'accept_requests',
#            'text_rules',
#            'file_rules',
#        )


class EventCreateForm(EditFormsMixin, TemplatedForm):

    class Meta:
        model = Event
        fields = (
            'type',
            'title',
            'start_date',
            'end_date',
            'requesting_till',
            'hold_place',
            'description',
            'text_rules',
            'file_rules',
        )


class EventUpdateForm(EditFormsMixin, TemplatedForm):

    class Meta:
        model = Event
        fields = (
            'title',
            'start_date',
            'end_date',
            'requesting_till',
            'hold_place',
            'description',
            'text_rules',
            'file_rules',
        )


class FestivalGroupForm(TemplatedForm):

    class Meta:
        model = FestivalGroup
        fields = (
            'title',
        )


class EventLogoEditForm(S3StorageFormMixin, forms.ModelForm):
    avatar_coords = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Event
        fields = ('logo',)


class NominationForm(TemplatedForm):

    class Meta:
        model = Nomination
        fields = (
            'title',
            'description',
            'age_from',
            'age_to'
        )


#class FestivalGeneralRuleForm(TemplatedForm):
#
#    class Meta:
#        model = FestivalGeneralRule
#        fields = (
#            'title',
#            'description',
#        )


    def __init__(self, request, event, *args, **kwargs):
        self.request = request
        self.event = event
        super(ParticipantForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.event = self.event
        return super(ParticipantForm, self).save(commit)


class ParticipantVideoForm(forms.ModelForm):

    class Meta:
        model = ParticipantVideo
        fields = (
            'age',
            'video',
            'nominations'
        )

    def __init__(self, *args, **kwargs):
        #TODO: need to select only event nominations in nominations field
        #TODO: need to select only current user videos in video
        super(ParticipantVideoForm, self).__init__(*args, **kwargs)
