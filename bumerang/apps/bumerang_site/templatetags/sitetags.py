# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from bumerang.apps.banners.models import MainPageBanner, CrossSiteBanner


register = template.Library()


@register.simple_tag()
def main_page_banner():
    banner = MainPageBanner.get_some()
    if banner:
        return banner
    return u"""
    <p>
        <a href="{0}">
            <img src="{1}i/banner.png" alt="Регистрация"
             width="200" height="340" />
        </a>
    </p>""".format(reverse('registration'), settings.STATIC_URL)


@register.simple_tag()
def cross_site_banners():
    banners_qs = CrossSiteBanner.objects.filter(is_active=True).order_by('-id')
    banners = u''
    for i in xrange(1, 4):
        try:
            banners += unicode(banners_qs.filter(position=i)[0])
        except IndexError:
            continue
    return banners
