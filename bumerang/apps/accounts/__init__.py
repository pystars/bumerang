# -*- coding: utf-8 -*-
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def remember_me_handler(sender, request, **kwargs):
    if 'remember_me' in request.POST:
        request.session[settings.KEEP_LOGGED_KEY] = True
