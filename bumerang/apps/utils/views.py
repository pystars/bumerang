# -*- coding: utf-8 -*-
import json
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseFormView
from django.views.generic.list import MultipleObjectMixin
from djangoratings.views import AddRatingView

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

    def form_valid(self, form):
        ids = json.loads(form.cleaned_data['ids'])
        ids = [i for i in ids if i]
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


class AjaxRatingView(AddRatingView):
    def __call__(self, request, model, app_label, object_id, field_name, score):
        """__call__(request, model, app_label, object_id, field_name, score)

        Adds a vote to the specified model field."""
        try:
            content_type = ContentType.objects.get(model=model, app_label=app_label)
        except ContentType.DoesNotExist:
            raise Http404('Invalid `model` or `app_label`.')


        response = super(AjaxRatingView, self).__call__(request,
            content_type.id,
            object_id, field_name, score)

        if response.status_code == 200:
            msg = {'error': False}
            if response.content == 'Vote recorded.':
                msg = {'error': False}
            if response.content == 'Vote changed.':
                msg = {'error': False}
        else:
            msg = {'error': True}

        return HttpResponse(json.dumps(msg), mimetype="application/json")
