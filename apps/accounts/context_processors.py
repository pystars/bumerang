# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm

def global_login_form(request):
    if not request.user.id:
        form = AuthenticationForm()
        return {'auth_form': form}
    else:
        return {}
