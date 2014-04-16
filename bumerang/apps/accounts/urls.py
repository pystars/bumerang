# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from bumerang.apps.accounts.forms import (
    ProfileResumeEditForm, FacultyForm, ServiceForm, TeammateForm, TeacherForm)
from bumerang.apps.accounts.models import Faculty, Service, Teammate, Teacher
from bumerang.apps.accounts.models import CustomUser as Profile
from bumerang.apps.accounts.views import (
    UsersListView, RegistrationFormView, PasswordRecoveryView, ProfileView,
    ProfileInfoEditView, ProfileAvatarEditView, ProfileUpdateView,
    ProfileSettingsEditView, AccountActivationView, FormsetUpdateView,
    ProfileVideoView, ProfilePhotoView, ProfileContactsEditView,
    RegisterEventRequestForm, ProfileEventListView)


urlpatterns = patterns('',
    url(r'^$',
        UsersListView.as_view(),
        name="users-list"),

    url(r'^members/$',
        UsersListView.as_view(),
        kwargs={'type': Profile.TYPE_USER},
        name="members-list"),

    url(r'^schools/$',
        UsersListView.as_view(),
        kwargs={'type': Profile.TYPE_SCHOOL},
        name="schools-list"),

    url(r'^studios/$',
        UsersListView.as_view(),
        kwargs={'type': Profile.TYPE_STUDIO},
        name="studios-list"),

    url(r'^register/$',
        RegistrationFormView.as_view(),
        name='registration'),

    url(r'^register-event-request/$',
        RegisterEventRequestForm.as_view(),
        name='register-event-request'),

    url(r'^login/$',
        'bumerang.apps.accounts.views.login',
        name='login'),

    url(r'^recover/$',
        PasswordRecoveryView.as_view(),
        name='password-recover'),

    url(r'^activate/(?P<code>\w{0,32})/$',
        AccountActivationView.as_view(),
        name='activate-account'),

    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        name='logout'),

    url(r'^profile/$',
        login_required(ProfileView.as_view()),
        name='profile-self'),

    url(r'^edit/$',
        login_required(ProfileInfoEditView.as_view()),
        name='profile-edit'),

    url(r'^edit-avatar/$',
        login_required(ProfileAvatarEditView.as_view(
            template_name_suffix='_edit_avatar')),
        name='profile-edit-avatar'),

    url(r'^edit-resume/$',
        login_required(ProfileUpdateView.as_view(
            form_class=ProfileResumeEditForm)),
        name='profile-edit-resume'),

    url(r'^edit-settings/$',
        login_required(ProfileSettingsEditView.as_view()),
        name='profile-edit-settings'),

    url(r'^edit-faculties/$',
        login_required(
            FormsetUpdateView.as_view(model=Faculty, form=FacultyForm)),
        name='profile-edit-faculties'),

    url(r'^edit-teachers/$',
        login_required(FormsetUpdateView.as_view(
            model=Teacher,
            form=TeacherForm,
            template_name="accounts/profile_teachers_formset.html")),
        name='profile-edit-teachers'),

    url(r'^edit-team/$',
        login_required(FormsetUpdateView.as_view(
            model=Teammate,
            form=TeammateForm,
            template_name="accounts/profile_team_formset.html")),
        name='profile-edit-team'),

    url(r'^edit-services/$',
        login_required(FormsetUpdateView.as_view(
            model=Service,
            form=ServiceForm,)),
        name='profile-edit-services'),

    url(r'^edit-contacts/$',
        login_required(ProfileContactsEditView.as_view()),
        name='profile-edit-contacts'),

    url(r'^(?P<pk>[\d]+)/$',
        ProfileView.as_view(),
        name='profile-detail'),

    url(r'^(?P<pk>[\d]+)/video/$',
        ProfileVideoView.as_view(template_name_suffix='_video'),
        name='profile-video-detail'),

    url(r'^(?P<pk>[\d]+)/photo/$',
        ProfilePhotoView.as_view(template_name_suffix='_photo'),
        name='profile-photo-detail'),

    url(r'^(?P<pk>[\d]+)/events/$',
        ProfileEventListView.as_view(),
        name='profile-event-list'),

    (r'^messages/', include('bumerang.apps.messages.urls')),
)