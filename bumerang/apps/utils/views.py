# -*- coding: utf-8 -*-
import json
from copy import copy

from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelformset_factory
from django.http import (HttpResponse, HttpResponseForbidden, Http404,
    HttpResponseRedirect)
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseFormView
from django.views.generic.list import MultipleObjectMixin
from djangoratings.views import AddRatingView

from bumerang.apps.utils.forms import ManyObjectsForm


class AjaxView(object):
    def get(self, request, **kwargs):
        return HttpResponseForbidden()

    def render_to_response(self, **kwargs):
        return HttpResponse(json.dumps(kwargs), mimetype="application/json")


class OwnerMixin(object):
    def get_queryset(self):
        # Если владелец - текущий пользователь, выбирутся
        # все объекты, иначе ни одного
        return super(OwnerMixin, self).get_queryset().filter(
            owner=self.request.user)


class ObjectsDeleteView(AjaxView, OwnerMixin, BaseFormView,
        MultipleObjectMixin):
    form_class = ManyObjectsForm

    def get_queryset(self, **kwargs):
        return super(ObjectsDeleteView, self).get_queryset().filter(**kwargs)

    def form_valid(self, form):
        ids = json.loads(form.cleaned_data['ids'])
        ids = [i for i in ids if i]
        objects = self.get_queryset(id__in=ids)
#        if objects.count() > 1:
#            msg = u'{0} успешно удалены'.format(
#                self.model._meta.verbose_name_plural)
#        else:
#            msg = u'{0} успешно удален'.format(self.model._meta.verbose_name)
        msg = u'Удалено объектов: {0}'.format(len(ids))

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
            content_type = ContentType.objects.get(
                model=model, app_label=app_label)
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

    @permission_required('djangoratings.add_vote')
    def dispatch(self, *args, **kwargs):
        return super(AjaxRatingView, self).dispatch(*args, **kwargs)


class GenericFormsetWithFKUpdateView(UpdateView):
    """
    Generic view save a formset of objects that contains relation to other
    """
    model = None
    formset_model = None
    formset_form_class = None
    add_item_text = None

    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            can_delete=True
        )
        self.model_name = self.model.__name__.lower()
        self.formset_prefix = self.formset_model.__name__.lower() + '_set'

    def get_context_data(self, **kwargs):
        object = self.get_object()
        self.qs = self.formset_model.objects.filter(**{self.model_name: object})
        ctx = {
            self.model_name: object,
            'formset': self.ModelFormSet(queryset=self.qs,
                prefix=self.formset_prefix),
            'add_item_text': self.add_item_text,
        }
        ctx.update(kwargs)
        return ctx

    def get_success_url(self):
        return self.request.path

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.ModelFormSet(request.POST, request.FILES,
            prefix=self.formset_prefix)
        if formset.is_valid():
            instances = formset.save(commit=False)
            object = self.get_object()
            for instance in instances:
                #the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, object)
                instance.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))


class SortingMixin(object):
    """
    Mixin for simple adding sorting in ListView

    need to setup sort_fields and DEFAULT_SORT_FIELD

    template must include 'snippets/sort_controls.html'
    """
    SORT_DIRECTION_PARAM = 'sort_direction'
    SORT_FIELD_PARAM = 'sort_field'
    DEFAULT_SORT_DIRECTION = 'asc'
    DEFAULT_SORT_FIELD = 'id'
    SORT_DIRECTIONS = {'asc', 'desc'}
    sort_fields = [
        ('id', u'по умолчанию'),
    ]

    def get_queryset(self):
        order = self.sort_field
        if self.sort_direction == 'desc':
            order = '-' + order
        return super(SortingMixin, self).get_queryset().order_by(order)

    def set_current_sort_params(self):
        self.sort_direction = self.params.pop(self.SORT_DIRECTION_PARAM,
            self.DEFAULT_SORT_DIRECTION)
        if self.sort_direction not in self.SORT_DIRECTIONS:
            self.sort_direction = self.DEFAULT_SORT_DIRECTION
        self.sort_field = self.params.pop(self.SORT_FIELD_PARAM,
            self.DEFAULT_SORT_FIELD)
        if self.sort_field not in [i[0] for i in self.sort_fields]:
            self.sort_field = self.DEFAULT_SORT_FIELD

    def _invert_sort(self, sort_direction):
        return list(self.SORT_DIRECTIONS - {sort_direction})[0]

    def get_sort_params(self):
        sort_params = []
        for field, name in self.sort_fields:
            uri_params = [self.request.path]
            sort_direction = self.DEFAULT_SORT_DIRECTION
            get_params = copy(self.params)
            sort_param = {'name': name, self.SORT_FIELD_PARAM: field}
            if self.sort_field == field:
                sort_param['is_current'] = True
                if self.sort_direction == self.DEFAULT_SORT_DIRECTION:
                    sort_direction = self._invert_sort(self.sort_direction)
                    get_params[self.SORT_DIRECTION_PARAM] = sort_direction
            else:
                sort_param['is_current'] = False
            if field != self.DEFAULT_SORT_FIELD:
                get_params[self.SORT_FIELD_PARAM] = field
            sort_param[self.SORT_DIRECTION_PARAM] = sort_direction
            get_string = u'&'.join([u'{0}={1}'.format(*param)
                                    for param in get_params.iteritems()])
            if get_string:
                uri_params.append(get_string)
            sort_param['url'] = u'?'.join(uri_params)
            sort_params.append(sort_param)
        return sort_params

    def get_context_data(self, **kwargs):
        ctx = super(SortingMixin, self).get_context_data(**kwargs)
        ctx['sort_params'] = self.get_sort_params()
        return ctx

    def get(self, request, *args, **kwargs):
        self.params = dict(request.REQUEST)
        self.set_current_sort_params()
        return super(SortingMixin, self).get(request, *args, **kwargs)
