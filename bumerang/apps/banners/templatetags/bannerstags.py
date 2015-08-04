# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from bumerang.apps.banners.models import MainPageBanner, CrossSiteBanner, \
    BumTVBanner

register = template.Library()


@register.simple_tag()
def bumtv_home_page_banners():
    return u"".join(map(unicode, BumTVBanner.objects.filter(is_active=True)))
