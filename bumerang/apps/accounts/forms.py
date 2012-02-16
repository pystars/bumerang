# -*- coding: utf-8 -*-
from uuid import uuid4
import random

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django import forms

from bumerang.apps.accounts.models import Profile, Faculty, Service, Teammate


class InfoEditFormsMixin(forms.ModelForm):
    '''
    Миксин, добавляющий стилизацию полей формы
    '''
    def __init__(self, *args, **kwargs):
        super(InfoEditFormsMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.TextInput
                or field.widget.__class__ == forms.widgets.PasswordInput
                or field.widget.__class__ == forms.widgets.DateInput):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide'
                else:
                    field.widget.attrs.update({'class': 'wide'})
            if (field.widget.__class__ == forms.widgets.Textarea):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide wide_about'
                else:
                    field.widget.attrs.update({'class': 'wide wide_about'})


class EditFormsMixin(forms.ModelForm):
    '''
    Миксин, добавляющий стилизацию полей формы
    '''
    def __init__(self, *args, **kwargs):
        super(EditFormsMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.TextInput
                or field.widget.__class__ == forms.widgets.PasswordInput):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide'
                else:
                    field.widget.attrs.update({'class': 'wide'})
            if (field.widget.__class__ == forms.widgets.Textarea):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide wide_descr2'
                else:
                    field.widget.attrs.update({'class': 'wide wide_descr2'})


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.TextInput
            or field.widget.__class__ == forms.widgets.PasswordInput):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' medium'
                else:
                    field.widget.attrs.update({'class': 'medium'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_(
                "The two password fields didn't match."))
        return password2

    def clean_email(self):
        '''
        Мы не можем изменить модель пользователя для указания
        уникальности поля email, а стороннее вмешательство в БД
        это не Ъ. Поэтому просто проводим
        выборку по указанному адресу. Процедура регистрации
        вызывается редко и не должна стать причиной излишней нагрузки
       '''
        email = self.cleaned_data.get('email', '')
        try:
            Profile.objects.get(email=email)
            raise forms.ValidationError(
                'Пользователь с таким адресом уже существует.')
        except ObjectDoesNotExist:
            return email

    def save(self, commit=True):
        profile = super(RegistrationForm, self).save(commit=False)
#        algo = 'sha1'
#        salt = get_hexdigest(
#            algo, str(random.random()), str(random.random()))[:5]
#        hsh = get_hexdigest(algo, salt, self.cleaned_data['password1'])
#        profile.password = '%s$%s$%s' % (algo, salt, hsh)
#        profile.username = uuid4().get_hex()[:30]
        profile.set_password(self.cleaned_data['password1'])
        if commit:
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ('email', 'type')
        widgets = {'type': forms.RadioSelect()}


class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        try:
            profile = Profile.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError(u'Пользователь с таким адресом не существует')


class ProfileInfoEditForm(InfoEditFormsMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'title',
            'nickname',
            'country',
            'region',
            'city',
            'birthday',
            'gender',
            'description',
        )


class ProfileAvatarEditForm(forms.ModelForm):
    avatar_coords = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Profile
        fields = ('avatar', 'avatar_coords',)


class ProfileResumeEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('work_type', 'work_company', 'schools', 'courses',
            'hobby', 'fav_movies', 'fav_music', 'fav_books')


class ProfileEmailEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('email',)


class UserProfileInfoForm(InfoEditFormsMixin, forms.ModelForm):
    '''
    Форма редактирования профиля пользователя
    '''
    title = forms.CharField(max_length=255, label=u'Имя, фамилия')
    description = forms.CharField(label=u'О себе', required=False,
        widget=forms.Textarea)

    class Meta:
        model = Profile
        fields = (
            'title',
            'nickname',
            'country',
            'region',
            'city',
            'birthday',
            'description',
            )


class SchoolProfileInfoForm(EditFormsMixin, forms.ModelForm):
    '''
    Форма редактирования профиля школы
    '''
    title = forms.CharField(max_length=255, label=u'Название')
    description = forms.CharField(label=u'О себе', widget=forms.Textarea)
    class Meta:
        model = Profile
        fields = ('title', 'country',
                  'region',
                  'city', 'description',)


class FacultyForm(EditFormsMixin, forms.ModelForm):
    '''
    Форма редактирования одного факультета
    '''
    class Meta:
        model = Faculty
        fields = ('title', 'description')


class ServiceForm(EditFormsMixin, forms.ModelForm):
    '''
    Форма редактирования одной услуги
    '''
    class Meta:
        model = Service
        fields = ('title', 'description')


class TeammateForm(EditFormsMixin, forms.ModelForm):
    class Meta:
        model = Teammate
        fields = ('photo', 'name', 'description')


class TeacherForm(EditFormsMixin, forms.ModelForm):
    class Meta:
        model = Teammate
        fields = ('photo', 'name', 'description')


class StudioProfileInfoForm(InfoEditFormsMixin, forms.ModelForm):
    '''
    Форма редактирования профиля студии
    '''
    title = forms.CharField(max_length=255, label=u'Название')
    description = forms.CharField(widget=forms.Textarea, label=u'Описание')
    class Meta:
        model = Profile
        fields = ('title', 'country',
                  'region',
                  'city', 'description', )


#class StudioProfileServicesForm(forms.ModelForm):
#    '''
#    Форма редактирования услуг студии
#    '''
#    class Meta:
#        model = Profile
#        fields = ('services',)


#class StudioProfileTeamForm(forms.ModelForm):
#    '''
#    Форма редактирования команды студии
#    '''
#    class Meta:
#        model = Profile
#        fields = ('team',)
