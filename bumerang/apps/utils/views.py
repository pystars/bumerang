# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseFormView
from django.views.generic.list import MultipleObjectMixin

from forms import ManyObjectsForm


class AjaxView(object):
    def get(self, request, **kwargs):
        return HttpResponseForbidden()

    def render_to_response(self, **kwargs):
        return HttpResponse(json.dumps(kwargs), mimetype="application/json")


class OwnerMixin(object):
    def get_queryset(self):
        # Если владелец - текущий пользователь, выбирутся
        # все видео. Иначе ни одного, удалять будет нечего.
        # И пусть хацкеры ломают головы ;)
        return super(OwnerMixin, self).get_queryset().filter(
            owner=self.request.user)


class ObjectsDeleteView(AjaxView, OwnerMixin, BaseFormView, MultipleObjectMixin):
    form_class = ManyObjectsForm

    def get_queryset(self, **kwargs):
        return super(ObjectsDeleteView, self).get_queryset().filter(**kwargs)

#    def post(self, request, *args, **kwargs):
#        return super(ObjectsDeleteView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        ids = json.loads(form.cleaned_data['ids'])
        objects = self.get_queryset(id__in=ids)
        if objects.count() > 1:
            msg = u'{0} успешно удалены'.format(
                self.model._meta.verbose_name_plural)
        else:
            msg = u'{0} успешно удален'.format(self.model._meta.verbose_name)
        for object in objects.all():
            object.delete()
        return super(ObjectsDeleteView, self).render_to_response(message=msg)


class XMLDetailView(DetailView):
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/xml'
        return super(XMLDetailView, self).render_to_response(context,
            **response_kwargs)
