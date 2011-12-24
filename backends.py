# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, check_password

from apps.accounts.models import Profile

class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            #user = Profile.objects.get(e_mail=username)
            profile = Profile.objects.get(e_mail=username)
            if profile.check_password(password):
                return profile
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None