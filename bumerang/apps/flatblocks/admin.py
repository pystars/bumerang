from django.contrib import admin
from django.contrib.sites.models import get_current_site, Site

from .models import FlatBlock


class FlatBlockAdmin(admin.ModelAdmin):
    ordering = ['slug', ]
    list_display = ('slug', 'header')
    search_fields = ('slug', 'header', 'content')
    exclude = ['site']

    def get_queryset(self, request):
        return super(FlatBlockAdmin, self).get_queryset(request).filter(
            site=get_current_site(request))

    def save_form(self, request, form, change):
        obj = form.save(commit=False)
        try:
            obj.site
        except Site.DoesNotExist:
            obj.site = get_current_site(request)
        return obj


admin.site.register(FlatBlock, FlatBlockAdmin)
