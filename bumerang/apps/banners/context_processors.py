# -*- coding: utf-8 -*-
from bumerang.apps.banners.models import HeadBanner


def header_banner(request):
    try:
        return {'header_banner': HeadBanner.objects.filter(
            is_active=True).order_by('-id')[0]}
    except IndexError:
        return {}
