# -*- coding: utf-8 -*-

from django.contrib.auth.forms import UserCreationForm
from django import forms

from apps.accounts.models import Profile


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.TextInput or field.widget.__class__ == forms.widgets.PasswordInput:
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' medium'
                else:
                    field.widget.attrs.update({'class':'medium'})

    """ Require email address when a user signs up """
    #email = forms.EmailField(label=u'E-mail', max_length=75)


    class Meta:
        model = Profile
        fields = ('e_mail', 'type')
        widgets = {
            #'e_mail': StyledTextInput(),
            'type': forms.RadioSelect()
        }


    '''
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError("This email address already exists. Did you forget your password?")
        except User.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        user.is_active = True # change to false if using email activation
        if commit:
            user.save()

        return user
    '''