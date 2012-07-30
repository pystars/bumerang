# -*- coding: utf-8 -*-
from django import forms
from django.db.utils import IntegrityError
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm, ModelChoiceField
from django.forms.widgets import Select, SelectMultiple, RadioSelect

from bumerang.apps.events.models import (Event, FestivalGroup, Nomination,
    ParticipantVideo, GeneralRule, NewsPost, Juror, Participant)
from bumerang.apps.utils.forms import (S3StorageFormMixin, TemplatedForm,
    EditFormsMixin, SelectList)
from bumerang.apps.video.models import Video


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
from bumerang.apps.video.models import Video


class EventCreateForm(EditFormsMixin, TemplatedForm):
    type = forms.ChoiceField(choices=Event.TYPES_CHOICES, label=u'Тип события')

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


class GeneralRuleForm(TemplatedForm):

    class Meta:
        model = GeneralRule
        fields = (
            'title',
            'description',
        )


class NewsPostForm(TemplatedForm):

    class Meta:
        model = NewsPost
        fields = (
            'title',
            'description',
        )


class JurorForm(TemplatedForm):

    class Meta:
        model = Juror
        fields = (
            'email',
            'info_second_name',
            'info_name',
            'info_middle_name',
            'min_avatar',
        )


class ParticipantVideoForm(ModelForm):
    """
    before using this modelform, we need to setup class:
    event and request needed for properly work
    """

    class Meta:
        model = ParticipantVideo
        fields = (
            'age',
            'video',
            'nominations'
        )

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoForm, self).__init__(*args, **kwargs)
        self.fields['nominations'] = forms.ModelChoiceField(
            label=u'Номинации', queryset=self.event.nomination_set.all(),
            widget=RadioSelect, empty_label=None)

        self.fields['video'] = forms.ModelChoiceField(
            label=u'Видео',
            queryset=Video.objects.filter(
            owner=self.request.user))


class ParticipantVideoFormForEventOwner(ParticipantVideoForm):
    """
    before using this modelform, we need to setup class:
    event and request needed for properly work
    """

    class Meta(ParticipantVideoForm.Meta):
        widgets = {
            'nominations': SelectMultiple
        }


class ParticipantApproveForm(ModelForm):

    class Meta:
        model = Participant
