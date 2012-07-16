# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm

def global_login_form(request):
    if request.user.is_anonymous():
        return {'auth_form': AuthenticationForm()}
    return {}
