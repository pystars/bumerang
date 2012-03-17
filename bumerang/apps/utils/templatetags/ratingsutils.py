# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import safe

register = template.Library()

@register.filter()
def render_rating(rating):

    item_tpl = u'''
        <li>
            <a href="#" data-rate="{0}" class="{1}">&nbsp;</a>
        </li>'''

    tpl = ""
    rating_integer = int(rating.instance.rating.get_rating())

    for i in range(1, rating.field.range+1):
        tpl += item_tpl.format(i, "active" if i <= rating_integer else "")

    return safe(tpl)

@register.filter()
def render_inactive_rating(rating):

    item_tpl = u'''
        <li>
            <b class="{1}">&nbsp;</b>
        </li>'''

    tpl = ""
    rating_integer = int(rating.instance.rating.get_rating())

    for i in range(1, rating.field.range+1):
        tpl += item_tpl.format(i, "active" if i <= rating_integer else "")

    return safe(tpl)