# -*- coding: utf-8 -*-
from uuid import uuid4
import random

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import get_hexdigest
from django.utils.translation import ugettext_lazy as _
from django import forms

from apps.accounts.models import Profile
from apps.video.models import VideoAlbum, Video


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
        profile = super(RegistrationForm, self).save(commit=False)

        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, profile.password)
        profile.password = '%s$%s$%s' % (algo, salt, hsh)
        profile.username = uuid4().get_hex()[:30]
        profile.email = profile.e_mail
        if commit:
            profile.save()
        return profile


    class Meta:
        model = Profile
        fields = ('e_mail', 'type')
        widgets = {
            'type': forms.RadioSelect()
        }


#TODO: Перенести email пользователя в модель User из профиля
class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        try:
            profile = Profile.objects.get(e_mail=email)
        except ObjectDoesNotExist:
            raise ValidationError(u'Пользователь с таким адресом не существует')


class VideoAlbumForm(forms.ModelForm):
    class Meta:
        model = VideoAlbum
        fields = ('title', 'description')


class VideoCreateForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'original_file', 'category', 'description')


class VideoUpdateForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'original_file', 'description', 'album')

    def __init__(self, *args, **kwargs):
        super(VideoUpdateForm, self).__init__(*args, **kwargs)



class ProfileInfoEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'title',
            'nickname',
            'place',
            'birthday',
            'gender',
            'description',
        )

class ProfileAvatarEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'avatar',
        )


class ProfileResumeEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'work',
            'education',
            'interests',
        )