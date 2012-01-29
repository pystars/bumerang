# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.filter
def field_type(value):
    return value.field.__class__.__name__

@register.filter()
def widget_type(value):
    return value.field.widget.__class__.__name__

@register.filter()
def form_type(value):
    return value.__class__.__name__
