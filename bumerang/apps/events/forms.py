# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from django.forms.widgets import Textarea, TextInput, RadioSelect, Select

from bumerang.apps.events.models import (Event, Nomination, ParticipantVideo,
    GeneralRule, NewsPost, Juror, Participant)
from bumerang.apps.utils.forms import (S3StorageFormMixin, TemplatedForm,
    EditFormsMixin, WideTextareaMixin)


class EventCreateForm(WideTextareaMixin, ModelForm):
    type = forms.ChoiceField(choices=Event.TYPES_CHOICES,
        label=u'Тип события', widget=forms.RadioSelect)

    class Meta:
        model = Event
        fields = (
            'type',
            'title',
            'parent',
            'start_date',
            'end_date',
            'requesting_till',
            'hold_place',
            'description',
#            'text_rules',
#            'file_rules',
            'contacts_raw_text',
        )
        widgets = {
            'title': TextInput(attrs={'class': 'medium'}),
        }

    def __init__(self, request, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        self.fields['type'].empty_label = None

        festivals_qs = request.user.owned_events.filter(is_approved=True,
            type=Event.FESTIVAL)
        if festivals_qs.count():
            self.fields['parent'].queryset = festivals_qs
            self.fields['parent'].empty_label = u'Не связан с фестивалем'
        else:
            del self.fields['parent']


class EventUpdateForm(TemplatedForm):

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
            'age_from',
            'age_to',
            'sort_order',
        )
        widgets = {
            'age_from': TextInput(attrs={ 'size': 2, 'maxlength': 2 }),
            'age_to': TextInput(attrs={ 'size': 2, 'maxlength': 2 }),
        }


class GeneralRuleForm(EditFormsMixin, ModelForm):

    class Meta:
        model = GeneralRule
        fields = (
            'title',
            'description',
        )


class NewsPostForm(EditFormsMixin, TemplatedForm):

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


class ParticipantForm(forms.Form):
    accepted = forms.BooleanField(required=True, error_messages={
        'required': u'''Вы должны ознакомиться и согласиться
                    с условиями подачи заявки.'''
    })


class ParticipantVideoForm(ModelForm):
    """
    before using this modelform, we need to setup class:
    event and request needed for properly work
    """

    class Meta:
        model = ParticipantVideo
        fields = (
            'video',
            'nomination',
            'age',
        )
        widgets = {
            'video': Select(attrs={'class': 'medium-select'}),
            'nomination': Select(attrs={'class': 'medium-select'}),
            'age': TextInput(attrs={'size': 2, 'maxlength': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoForm, self).__init__(*args, **kwargs)
        self.fields['nomination'].queryset = self.event.nomination_set.all()
        self.fields['nomination'].empty_label = None
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
