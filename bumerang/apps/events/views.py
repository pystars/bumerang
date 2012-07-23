# -*- coding: utf-8 -*-
from __future__ import division
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import json
from PIL import Image
from django.db.utils import IntegrityError
from django.forms.models import modelformset_factory
from django.views.generic.edit import CreateView
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
from django.forms.util import ErrorList
from django.views.generic import ListView, UpdateView, View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import DetailView

from bumerang.apps.accounts.models import Profile
from bumerang.apps.accounts.views import notify_success, notify_error
from bumerang.apps.events.models import (Event, Nomination, Participant,
    ParticipantVideo)
from bumerang.apps.events.forms import (FestivalGroupForm, EventCreateForm,
    EventUpdateForm, EventLogoEditForm, NominationForm, ParticipantForm,
    ParticipantVideoForm)
from bumerang.apps.utils.views import (OwnerMixin,
    GenericFormsetWithFKUpdateView)


class EventListView(ListView):
    model = Event
    paginate_by = 10

    def get_queryset(self):
        return super(EventListView, self).get_queryset().filter(
            is_approved=True)


class EventEditMixin(UpdateView):
    model = Event

    def _get_profile(self, request):
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            return Profile()

    def get_context_data(self, **kwargs):
        profile = self._get_profile(self.request)
        festival = self.get_object()

        if festival.owner != profile:
            raise PermissionDenied

        context = {
            'profile': profile,
            'festival': festival,
        }
        context.update(kwargs)
        return context


class EventCreateView(TemplateResponseMixin, View):
    template_name = 'events/event_send_request.html'
    group_form_class = FestivalGroupForm
    event_form_class = EventCreateForm

    def get_context_data(self, **kwargs):
        ctx = {
            'group_form': self.group_form_class(prefix='group'),
            'event_form': self.event_form_class(prefix='event'),
        }
        ctx.update(kwargs)
        return ctx

    def forms_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        group_form =self.group_form_class(request.POST, prefix='group')
        event_form = self.event_form_class(
            request.POST, request.FILES, prefix='event')

        if event_form.is_valid():
            event = event_form.save(commit=False)
            if event.type == Event.FESTIVAL:
                if group_form.is_valid():
                    group = group_form.save(commit=False)
                    group.owner = request.user
                    group.save()
                    event.group = group
                else:
                    self.forms_invalid(
                        group_form=group_form, event_form=event_form)
            event.owner = request.user
            event.save()

            self.template_name = \
                'events/event_send_request_sended.html'
            return self.render_to_response(self.get_context_data())
        else:
            return self.forms_invalid(
                group_form=group_form, event_form=event_form)


class EventDetailView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = kwargs
        festivals_archive = Event.objects.filter(
            group=self.get_object().group).order_by('start_date')
        context.update({'festivals_archive': festivals_archive})
        return context

#class EventEditInfoView(EventEditMixin):
class EventEditInfoView(OwnerMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm

    def get_success_url(self):
        return reverse('event-edit-info', kwargs = { 'pk': self.object.pk })


class EventEditLogoView(OwnerMixin, UpdateView):
    model = Event
    form_class = EventLogoEditForm
    template_name = "events/event_edit_logo.html"

    def get_success_url(self):
        return reverse('event-edit-logo', kwargs = {'pk': self.object.pk})

    def form_valid(self, form):
        MAX_WIDTH = 500

        try:
            coords = json.loads(form.cleaned_data['avatar_coords'])
        except ValueError:
            coords = {
                'x': 0,
                'y': 0,
                'x2': 175,
                'y2': 175,
                }
            # Загружен ли уже аватар и мы только должны его обрезать?
        img = Image.open(self.request.FILES.get('logo', self.object.logo))
        img = img.convert('RGB')

        # Если загружаемый аватар слишком маленький
        if img.size[0] < 175 or img.size[1] < 175:
            form_errors = form._errors.setdefault('logo', ErrorList())
            form_errors.append(
                u'Размер изображения должен быть больше 175x175 пикселей.')

            notify_error(self.request, message=u'''
            Произошла ошибка при обновлении логотипа.
            Размер изображения должен быть больше 175x175 пикселей.''')
            return self.render_to_response(self.get_context_data(form=form))

        # Если изображение слишком широкое, ужимаем
        if img.size[0] > MAX_WIDTH:
            aspect = img.size[0] / MAX_WIDTH
            new_height = int(round(img.size[1] / aspect))
            # Вот с этим изображением мы и будем работать
            img = img.resize((MAX_WIDTH, new_height), Image.ANTIALIAS)

        # Иначе просто обрезаем
        cropped_image = img.crop((coords['x'],
                                  coords['y'],
                                  coords['x2'],
                                  coords['y2']))
        cropped_image.thumbnail((175, 175), Image.ANTIALIAS)

        temp_handle = StringIO()
        cropped_image.save(temp_handle, 'jpeg', quality=100)
        temp_handle.seek(0)

        suf = SimpleUploadedFile('min.jpg',
            temp_handle.read(), content_type='image/jpg')

        self.object.min_logo.save('min.jpg', suf, save=False)
        form.save()

        notify_success(self.request,
            message=u'Логотип успешно обновлен.')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        notify_error(self.request, message=u'''
            Произошла ошибка при обновлении логотипа.
            Возможно, файл, который вы загрузили, поврежден
            или не является изображением.
        ''')

        return self.render_to_response(self.get_context_data(form=form))


class EventNominationsUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model=Event
    formset_model=Nomination
    formset_form_class=NominationForm
    template_name="events/event_edit_formset.html"
    add_item_text=u'Добавить номинацию'


class ParticipantCreateView(CreateView):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"
    template_name = 'events/participant_form.html'

    def __init__(self, **kwargs):
#        self.object = None
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            can_delete=True
        )
        self.model_name = self.model.__name__.lower()

    def get_context_data(self, **kwargs):
        self.event = Event.objects.get(id=self.kwargs['pk'])
        context = {
            'formset': self.ModelFormSet(prefix='participantvideo'),
            'add_item_text': self.add_item_text,
            'event': self.event
        }
        context.update(kwargs)
        return context

    def get_success_url(self):
        return reverse('participant-edit', args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.event = Event.objects.get(id=self.kwargs['pk'])
        formset = self.ModelFormSet(request.POST, prefix='participantvideo')
        if formset.is_valid():
            self.object = self.model(owner=request.user, event=self.event)
            try:
                self.object.save()
            except IntegrityError:
                try:
                    self.object = self.model.objects.get(event=self.event,
                        owner=request.user)
                    return HttpResponseRedirect(self.get_success_url())
                except request.user.DoesNotExist:
                    return self.render_to_response(
                        self.get_context_data(formset=formset))
            instances = formset.save(commit=False)
            for instance in instances:
                instance.participant = self.object
                instance.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(formset=formset))


class ParticipantUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"
    template_name = 'events/participant_form.html'

    def get_context_data(self, **kwargs):
        context = super(ParticipantUpdateView, self).get_context_data(**kwargs)
        context.update({'event': Event.objects.get(id=self.kwargs['pk'])})
        return context
