# -*- coding: utf-8 -*-
from django.contrib import admin

from models import PhotoAlbum, PhotoCategory
from bumerang.apps.utils.admin import TitleSlugAdmin


admin.site.register(PhotoCategory, TitleSlugAdmin)
admin.site.register(PhotoAlbum)
