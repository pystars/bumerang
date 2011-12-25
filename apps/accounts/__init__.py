# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_in

import settings

@receiver(user_logged_in)
def remember_me_handler(sender, request, **kwargs):
    if 'remember_me' in request.POST:
        request.session[settings.KEEP_LOGGED_KEY] = True