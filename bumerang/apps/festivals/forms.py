# -*- coding: utf-8 -*-
from django.forms.fields import ChoiceField
from os.path import basename
from django import forms
from django.forms import CheckboxInput
from django.forms.forms import BoundField
from django.forms.util import flatatt
from django.forms.widgets import Textarea, ClearableFileInput, \
    TextInput, DateInput, HiddenInput
from django.template import loader
from django.template.context import Context
from django.utils.safestring import mark_safe

from bumerang.apps.festivals.models import Festival, FestivalGroup, FestivalNomination, FestivalGeneralRule, FestivalRequestVideo, FestivalRequest
from bumerang.apps.utils.forms import S3StorageFormMixin


class EditFormsMixin(forms.ModelForm):
    u"""
    Миксин, добавляющий стилизацию полей формы
    """
    def __init__(self, *args, **kwargs):
        super(EditFormsMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.Textarea):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide wide_descr2'
                else:
                    field.widget.attrs.update({'class': 'wide wide_descr2'})


class TemplatedForm(forms.ModelForm):

    def _render_field(self, field):
        widget_type = field.field.widget.__class__
        template_name = str()

        ctx = Context({ 'data': {
            'label': field.label,
            'required': field.field.required,
            'attrs': flatatt(field.field.widget.attrs),
            'value': field.value(),
            'id': field.auto_id,
            'name': field.html_name,
            'errors': field.errors
            }
        })

        if widget_type == Textarea:
            template_name = 'accounts/forms/textarea.html'

        if widget_type == TextInput:
            template_name = 'accounts/forms/textinput.html'

        if widget_type == DateInput:
            template_name = 'accounts/forms/datetime.html'

        if widget_type == CheckboxInput:
            template_name = 'accounts/forms/checkbox.html'

        if widget_type == HiddenInput:
            template_name = 'accounts/forms/hiddeninput.html'

        if widget_type == ClearableFileInput:
            template_name = 'accounts/forms/fileinput.html'

            val = basename(field.value().name)

            file_text = u'Текущий загруженный файл: {0}'.format(val)
            ctx['data'].update({
                'file_text': file_text,
            })

        tpl = loader.get_template(template_name)
        return tpl.render(ctx)

    def template_form_render(self):
        bound_fields = [BoundField(self, field, name) for name, field\
                        in self.fields.items()]

        rendered_html = u''

        for field in bound_fields:
            rendered_html += self._render_field(field)

        return mark_safe(rendered_html)

    def __unicode__(self):
        return self.template_form_render()


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


class FestivalForm(EditFormsMixin, TemplatedForm):

    class Meta:
        model = Festival
        fields = (
            'name',
            'start_date',
            'end_date',
            'accept_requests_date',
            'hold_place',
            'description',
            'text_rules',
            'file_rules',
        )


class FestivalGroupForm(TemplatedForm):

    class Meta:
        model = FestivalGroup
        fields = (
            'name',
        )


class FestivalLogoEditForm(S3StorageFormMixin, forms.ModelForm):
    avatar_coords = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Festival
        fields = ('logo',)


class FestivalNominationForm(TemplatedForm):

    class Meta:
        model = FestivalNomination
        fields = (
            'name',
            'description',
        )


class FestivalGeneralRuleForm(TemplatedForm):

    class Meta:
        model = FestivalGeneralRule
        fields = (
            'title',
            'description',
        )


class FestivalRequestForm(forms.ModelForm):
    #videos = forms.MultipleChoiceField()

    class Meta:
        model = FestivalRequest
        fields = (
            'videos',
        )