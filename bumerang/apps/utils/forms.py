# -*- coding: utf-8 -*-
from posixpath import basename
from django import forms
from django.forms.fields import ClearableFileInput, FileField
from django.forms.forms import BoundField
from django.forms.util import flatatt
from django.forms.widgets import Select, Textarea
from django.template import Context
from django.template import loader
from django.utils.safestring import mark_safe


class ManyObjectsForm(forms.Form):
    ids = forms.CharField()


class S3StorageFormMixin(object):

    def save(self, commit=True):
        if commit:
            file_fields_set = set(f[0] for f in self.fields.items()
                                  if isinstance(f[1], FileField))
            for field in file_fields_set & set(self.changed_data):
                self.files[field].open()
        return super(S3StorageFormMixin, self).save(commit)


class SelectList(Select):
    def __init__(self, attrs=None, choices=()):
        super(SelectList, self).__init__(attrs, choices)


class TemplatedForm(forms.ModelForm):
    u"""
    Подменяет виджеты формы
    """

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
            'errors': field.errors,
            }
        })
        if widget_type == Select:
#            if field.field.required:
#                print field.field.choices[1:], 'required'
#                ctx['data']['choices'] = field.field.choices[1:]
#            else:
#                print field.field.choices
#                ctx['data']['choices'] = field.field.choices
            ctx['data']['choices'] = field.field.choices

        if widget_type == SelectList:
            ctx['data']['choices'] = field.field.choices

        template_name = 'utils/widgets/{0}.html'.format(
            widget_type.__name__.lower())

        if widget_type == ClearableFileInput:
            if field.value():
                val = basename(u'{0}'.format(field.value()))
                file_text = u'Текущий загруженный файл: {0}'.format(val)
                ctx['data'].update(file_text=file_text)

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


class EditFormsMixin(forms.ModelForm):
    u"""
    Миксин, добавляющий стилизацию полей формы
    """
    def __init__(self, *args, **kwargs):
        super(EditFormsMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.Textarea or \
               field.widget.__class__ == forms.widgets.TextInput:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' wide wide_descr2'
                else:
                    field.widget.attrs.update({'class': 'wide wide_descr2'})


class WideTextareaMixin(forms.ModelForm):
    """
    Makes wide only textarea fields
    """
    def __init__(self, *args, **kwargs):
        super(WideTextareaMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.Textarea:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' wide wide_descr2'
                else:
                    field.widget.attrs.update({'class': 'wide wide_descr2'})
