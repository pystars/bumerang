# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import (HttpResponse, HttpResponseForbidden, Http404,
    HttpResponseRedirect)
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseFormView, CreateView
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
#        for object in objects.all():
#            object.delete()
        objects.delete()
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

    @permission_required('djangoratings.add_vote')
    def dispatch(self, *args, **kwargs):
        return super(AjaxRatingView, self).dispatch(*args, **kwargs)


class GenericFormsetWithFKUpdateView(UpdateView):
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

    def get_context_data(self, **kwargs):
        context = kwargs
        object = self.get_object()
        qs = self.formset_model.objects.filter(**{self.model_name:object})
        context.update({
            self.model_name: object,
            'formset': self.ModelFormSet(queryset=qs),
            'add_item_text': self.add_item_text,
        })
        return context

    def get_success_url(self):
        return self.request.path

    def post(self, request, *args, **kwargs):
        formset = self.ModelFormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            object = self.get_object()
            for instance in instances:
                #the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, object)
                instance.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(formset=formset))


class GenericFormsetWithFKCreateView(CreateView):
    model = None
    form_class = None
    formset_model = None
    formset_form_class = None
    add_item_text = None
    object = None

    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            can_delete=True
        )
        self.model_name = self.model.__name__.lower()

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update({
            'form' : self.form_class(**self.get_form_kwargs()),
            'formset': self.ModelFormSet(),
            'add_item_text': self.add_item_text,
        })
        return context

    def get_success_url(self):
        return reverse('participant-edit', args=self.object.id,)#self.request.path

    def post(self, request, *args, **kwargs):
        form = self.form_class(**self.get_form_kwargs())
        formset = self.ModelFormSet(request.POST, request.FILES)
        print
        if form.is_valid() and formset.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = request.user
            self.object.save()
            instances = formset.save(commit=False)
            for instance in instances:
                #the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, self.object)
#                instance.save()
            self.formset_model.objects.bulk_create(instances)
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(
            form=form, formset=formset))
