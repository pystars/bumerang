# -*- coding: utf-8 -*-
from datetime import timedelta
from django.utils.encoding import force_unicode

from django.utils.translation import ugettext as _
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.forms.formsets import all_valid

from models import PlayList, PlayListItem, Channel
from bumerang.apps.video.models import Video


class PlayListItemAdmin(admin.TabularInline):
    model = PlayListItem
    readonly_fields = ['play_from', 'play_till', 'offset']
    ordering = ['sort_order', 'id']
    extra = 1


class PlayListAdmin(admin.ModelAdmin):

    inlines = [PlayListItemAdmin,]

    def save_formset(self, request, form, formset, change):
        formset.save()
        offset = 0
        for item in form.instance.playlistitem_set.all():
            item.offset = offset
            item.save()
            offset += item.video.duration
        form.instance.rotate_till = form.instance.rotate_from + timedelta(
            milliseconds=offset)
        form.instance.save()

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                    instance=new_object,
                    save_as_new="_saveasnew" in request.POST,
                    prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, False)
                self.save_related(request, form, formsets, False)
                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset_initial = []
                if issubclass(inline.model, PlayListItem):
                    for video in Video.objects.filter(is_in_broadcast_lists=True):
                        formset_initial.append({'video': video})
                formset = FormSet(instance=self.model(), prefix=prefix,
                    queryset=inline.queryset(request),
                    initial=formset_initial)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            prepopulated = dict(inline.get_prepopulated_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)


admin.site.register(Channel)
admin.site.register(PlayList, PlayListAdmin)
