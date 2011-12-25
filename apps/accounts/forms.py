# -*- coding: utf-8 -*-
from uuid import uuid4

from django.utils.translation import ugettext_lazy as _
from django import forms

from apps.accounts.models import Profile


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.TextInput\
            or field.widget.__class__ == forms.widgets.PasswordInput:
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' medium'
                else:
                    field.widget.attrs.update({'class':'medium'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        #user = super(UserCreationForm, self).save(commit=False)
        #user.set_password(self.cleaned_data["password1"])

        profile = super(RegistrationForm, self).save(commit=False)

        from django.contrib.auth.models import get_hexdigest
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, profile.password)
        profile.password = '%s$%s$%s' % (algo, salt, hsh)
        profile.username = uuid4().get_hex()[:30]
        if commit:
            profile.save()
        return profile


    class Meta:
        model = Profile
        fields = ('e_mail', 'type')
        #        exclude = ('username',)
        widgets = {
            #'e_mail': StyledTextInput(),
            'type': forms.RadioSelect()
        }