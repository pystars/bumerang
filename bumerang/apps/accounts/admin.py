# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Profile


class ProfileAdmin(admin.ModelAdmin):
    exclude = ('first_name', 'last_name', 'email')
    list_display = ('__unicode__', 'type', 'city', 'date_joined', 'username')
    prepopulated_fields = {'info_email': ['username'],}
    readonly_fields = ('show_avatar', 'last_login', 'date_joined')
    fieldsets = (
        ('Main params', {'fields': (
            'title',
            'type',
            'username',
            'password',
            ('is_active', 'is_staff', 'is_superuser'),
            ('last_login', 'date_joined'),
            'show_avatar',
            'birthday',
            'description',
        )}),
        ('Info params', {'fields': (
            ('country', 'region'),
            'city',
            'work_type',
            'work_company',
            'schools',
            'courses',
            'hobby',
            'fav_movies',
            'fav_music',
            'fav_books',
            'nickname',
            'gender',
            ('info_second_name', 'info_name'),
            'info_middle_name',
            'info_address',
            'info_postal_address',
            ('info_phone', 'info_mobile_phone'),
            'info_email',
            ('info_organization_form', 'info_organization')
        )})
    )

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


admin.site.register(Profile, ProfileAdmin)
