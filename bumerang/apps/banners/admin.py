# -*- coding: utf-8 -*-
from django.contrib import admin

from models import HeadBanner, MainPageBanner, EventBanner, CrossSiteBanner


class HeadBannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'text', 'is_active', 'create_date')
    list_editable = ['is_active']
    readonly_fields = ['create_date']
    list_display_links = ('name',)


class BannerAdminBase(admin.ModelAdmin):
    fieldsets = [
        [None, {'fields': ('name', 'is_active')}],
        ['image options', {'fields': ('url', 'alt', 'image')}],
        ['flash options', {'fields': ('flash',)}]
    ]
    list_display = ['name', 'is_active', 'create_date']
    list_editable = ['is_active']
    readonly_fields = ['create_date']
    list_display_links = ('name',)


class MainPageBannerAdmin(BannerAdminBase):
    fieldsets = BannerAdminBase.fieldsets + [['unique options', {'fields': ['weight']}]]


class EventBannerAdmin(BannerAdminBase):
    fieldsets = BannerAdminBase.fieldsets + [['unique options', {'fields': ['event']}]]


class CrossSiteBannerAdmin(BannerAdminBase):
    fieldsets = BannerAdminBase.fieldsets + [['unique options', {'fields': ['position']}]]
    list_display = BannerAdminBase.list_display + ['position']
    list_editable = ['is_active', 'position']



admin.site.register(HeadBanner, HeadBannerAdmin)
admin.site.register(MainPageBanner, MainPageBannerAdmin)
admin.site.register(EventBanner, EventBannerAdmin)
admin.site.register(CrossSiteBanner, CrossSiteBannerAdmin)
