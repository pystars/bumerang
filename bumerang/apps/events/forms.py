# -*- coding: utf-8 -*-
from django import forms
from django.forms import DateInput, CheckboxInput
from django.forms.models import ModelForm
from django.forms.widgets import Textarea, TextInput, RadioSelect, Select, Widget, SelectMultiple

from bumerang.apps.events.models import (Event, Nomination, ParticipantVideo,
    GeneralRule, NewsPost, Juror, Participant)
from bumerang.apps.utils.forms import (S3StorageFormMixin, TemplatedForm,
    EditFormsMixin, WideTextareaMixin)


class WidgetParametersMixin(Widget):
    def __init__(self, attrs=None, parameters=None):
        if attrs is not None:
            self.attrs = attrs.copy()
            self.parameters = parameters.copy()
        else:
            self.attrs = {}
            self.parameters = {}


class TextInputWidget(TextInput):
    def __init__(self, attrs=None, parameters=None):
        if attrs is not None:
            self.attrs = attrs.copy()
            self.parameters = parameters.copy()
        else:
            self.attrs = {}
            self.parameters = {}


two_symbols_widget = TextInput(attrs={
    'size': 2,
    'maxlength': 2,
    'class': 'zero-width-field',
})

two_symbols_table_widget = TextInputWidget(attrs={
    'size': 2,
    'maxlength': 2,
    'class': 'zero-width-field',
    }, parameters={
    'render_type': 'table',
})

date_widget = DateInput(attrs={
    'class': 'short',
    'input_formats': '%d.%m.%Y',
})


class EventCreateForm(WideTextareaMixin, ModelForm):
    type = forms.ChoiceField(choices=Event.TYPES_CHOICES,
        label=u'Тип события', widget=forms.RadioSelect)

    class Meta:
        model = Event
        fields = (
            'type',
            'parent',
            'title',
            'start_date',
            'end_date',
            'requesting_till',
            'hold_place',
            'description',
            'contacts_raw_text',
        )
        widgets = {
            'title': TextInput(attrs={'class': 'wide'}),
            'start_date': TextInput(attrs={'class': 'mini'}),
            'end_date': TextInput(attrs={'class': 'mini'}),
            'requesting_till': TextInput(attrs={'class': 'mini'}),
        }

    def __init__(self, request, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        self.fields['type'].empty_label = None
        self.fields['type'].default = None

        festivals_qs = request.user.owned_events.filter(is_approved=True,
            type=Event.FESTIVAL)
        if festivals_qs.count():
            self.fields['parent'].queryset = festivals_qs
            self.fields['parent'].empty_label = u'Не связан с фестивалем'
        else:
            del self.fields['parent']


class EventUpdateForm(WideTextareaMixin, TemplatedForm):

    class Meta:
        model = Event
        fields = (
            'title',
            'start_date',
            'end_date',
            'requesting_till',
            'hold_place',
            'description',
            'participant_conditions'
        )
        widgets = {
            'title': TextInput(attrs={'class': 'wide'}),
            'start_date': date_widget,
            'end_date': date_widget,
            'requesting_till': date_widget,
        }

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
            'title': TextInput(attrs={'class': 'medium'}),
            'age_from': two_symbols_widget,
            'age_to': two_symbols_widget,
            'sort_order': two_symbols_widget
        }


class GeneralRuleForm(EditFormsMixin, ModelForm):

    class Meta:
        model = GeneralRule
        fields = (
            'title',
            'description',
        )


class NewsPostForm(WideTextareaMixin, TemplatedForm):

    class Meta:
        model = NewsPost
        fields = (
            'title',
            'description',
        )
        widgets = {
            'title': TextInput(attrs={'class': 'wide'})
        }


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
        widgets = {
            'email': TextInput(attrs={'class': 'wide'}),
            'info_second_name': TextInput(attrs={'class': 'wide'}),
            'info_name': TextInput(attrs={'class': 'wide'}),
            'info_middle_name': TextInput(attrs={'class': 'wide'}),
        }


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
            'age': two_symbols_table_widget,
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoForm, self).__init__(*args, **kwargs)
        self.fields['nomination'].empty_label = None

        if self.request.user.is_authenticated():
            self.fields['nomination'].queryset = self.event.nomination_set.all()
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
        widgets = {
            'nominations': SelectMultiple(
                attrs={'class': 'medium-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantVideoReviewForm, self).__init__(*args, **kwargs)
        self.fields['nominations'].queryset = self.event.nomination_set.all()


class ParticipantApproveForm(ModelForm):

    class Meta:
        model = Participant
