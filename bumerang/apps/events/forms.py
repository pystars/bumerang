# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from django.forms.widgets import Textarea

from bumerang.apps.events.models import (Event, FestivalGroup, Nomination,
    ParticipantVideo, GeneralRule, NewsPost, Juror, Participant)
from bumerang.apps.utils.forms import (S3StorageFormMixin, TemplatedForm,
    EditFormsMixin)


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


class EventContactsUpdateForm(EditFormsMixin, TemplatedForm):
    contacts_raw_text = forms.CharField(label=u'Контакты',
        required=True, widget=Textarea)

    class Meta:
        fields = (
            'contacts_raw_text',
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
            'age_to',
            'sort_order',
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
            'nomination'
        )

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoForm, self).__init__(*args, **kwargs)
        self.fields['nomination'].queryset=self.event.nomination_set.all()
        self.fields['video'].queryset = self.fields['video'].queryset.filter(
            owner=self.request.user)


class ParticipantVideoReviewForm(ModelForm):
    """
    before using this modelform, we need to setup class:
    event and request needed for properly work
    """
    class Meta:
        model = ParticipantVideo
        fields = (
            'id',
            'nominations',
            'is_accepted'
        )

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoReviewForm, self).__init__(*args, **kwargs)
        self.fields['nominations'].queryset = self.event.nomination_set.all()


class ParticipantApproveForm(ModelForm):

    class Meta:
        model = Participant
