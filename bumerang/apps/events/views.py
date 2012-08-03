# -*- coding: utf-8 -*-
from __future__ import division
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import json
from PIL import Image
from django.db.utils import IntegrityError
from django.forms.models import modelformset_factory
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
from django.forms.util import ErrorList
from django.views.generic import ListView, View
from django.views.generic.base import TemplateResponseMixin
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404

from bumerang.apps.accounts.models import Profile
from bumerang.apps.accounts.views import notify_success, notify_error
from bumerang.apps.events.models import (Event, Nomination, Participant,
    ParticipantVideo, GeneralRule, NewsPost, Juror, VideoNomination)
from bumerang.apps.events.forms import (FestivalGroupForm, EventCreateForm,
    EventUpdateForm, EventLogoEditForm, NominationForm, ParticipantVideoForm,
    GeneralRuleForm, NewsPostForm, JurorForm, ParticipantVideoReviewForm,
    EventContactsUpdateForm, ParticipantForm)
from bumerang.apps.utils.views import (OwnerMixin, SortingMixin,
    GenericFormsetWithFKUpdateView)

"""
    Mixins classes
"""
class ParticipantMixin(object):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"
    template_name = 'events/participant_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if 'event_pk' in kwargs:
            self.event = Event.objects.get(id=kwargs['event_pk'])
        else:
            self.object = self.get_object()
            self.event = self.object.event
        self.formset_form_class.event = self.event
        self.formset_form_class.request = request
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            can_delete=True
        )
        return handler(request, *args, **kwargs)


"""
    App views classes
"""
class EventDetailView(DetailView):
    model = Event

    rel_model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context.update({
            'participant_form': ParticipantForm(prefix='accept',
                initial={ 'accepted': False }),
            'formset': self.ModelFormSet(prefix='participantvideo_set'),
            'add_item_text': self.add_item_text,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.formset_form_class.event = self.object
        self.formset_form_class.request = request
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            can_delete=True
        )

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class EventListView(SortingMixin, ListView):
    model = Event
    paginate_by = 10
    DEFAULT_SORT_FIELD = 'title'
    sort_fields = [
        ('title', u'по названию'),
        ('requesting_till', u'по дате приема заявок')
    ]

    def get_filter(self):
        if 'type' in self.kwargs:
            return {'type': self.kwargs['type']}
        return {}

    def get_queryset(self):
        return super(EventListView, self).get_queryset().filter(
            is_approved=True, **self.get_filter())


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


class EventPressListView(ListView):
    model = NewsPost

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return event.newspost_set.all().order_by('-pk' ,'-creation_date')

    def get_context_data(self, **kwargs):
        context = super(EventPressListView, self).get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        festivals_archive = Event.objects.filter(
            group=event.group).order_by('start_date')
        context.update({
            'event': event,
            'festivals_archive': festivals_archive
        })
        return context


class EventFilmsListView(ListView):
    model = ParticipantVideo
    template_name = 'events/films_list.html'
    paginate_by = 10

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        participants = event.participant_set.all()

        if 'nomination_pk' in self.kwargs:
            nomination = get_object_or_404(Nomination,
                id=self.kwargs['nomination_pk'])
        else:
            nomination = event.nomination_set.all()[0]

        films = ParticipantVideo.objects.filter(
            participant=participants,
            nominations=nomination
        )

        return films

    def get_context_data(self, **kwargs):
        context = super(EventFilmsListView, self).get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        festivals_archive = Event.objects.filter(
            group=event.group).order_by('start_date')

        try:
            nominations = event.nomination_set.all()
        except ObjectDoesNotExist:
            nominations = None

        if 'nomination_pk' in self.kwargs:
            nomination = event.nomination_set.get(
                pk=self.kwargs['nomination_pk'])
        else:
            nomination = event.nomination_set.all()[0]

        context.update({
            'event': event,
            'festivals_archive': festivals_archive,
            'nominations': nominations,
            'nomination': nomination
        })
        return context


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
    model = Event
    formset_model = Nomination
    formset_form_class = NominationForm
    template_name = "events/event_edit_formset.html"
    add_item_text = u'Добавить номинацию'


class EventGeneralRuleUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model = Event
    formset_model = GeneralRule
    formset_form_class = GeneralRuleForm
    template_name = "events/event_edit_formset.html"
    add_item_text = u'Добавить положение'


class EventJurorsUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model = Event
    formset_model = Juror
    formset_form_class = JurorForm
    template_name = "events/event_edit_formset.html"
    add_item_text = u'Добавить члена жюри'

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.ModelFormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            object = self.get_object()
            for instance in instances:
                try:
                    user = User.objects.get(username=instance.email)
                except User.DoesNotExist:
                    #TODO: create users for jurors
                    profile = Profile(
                        username = instance.email,
                        info_second_name = instance.info_second_name,
                        info_name = instance.info_name,
                        info_middle_name = instance.info_middle_name,
                        min_avatar = instance.min_avatar,
                    )
                    password = User.objects.make_random_password()
                    profile.set_password(password)
                    profile.save()
                    user = User.objects.get(pk=profile.id)
                    #TODO: send letter to new juror with links to password
                    # and event
                instance.user = user
                #the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, object)
                instance.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))



class EventNewsUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model = Event
    formset_model = NewsPost
    formset_form_class = NewsPostForm
    template_name = "events/event_edit_formset.html"
    add_item_text = u'Добавить новость'


class EventContactsUpdateView(UpdateView):
    model = Event
    form_class = EventContactsUpdateForm

    def get_success_url(self):
        return reverse('event-edit-contacts', kwargs = { 'pk': self.object.pk })


class ParticipantCreateView(ParticipantMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = {
            'participant_form': ParticipantForm(prefix='accept',
                initial={ 'accepted': False }),
            'formset': self.ModelFormSet(prefix='participantvideo_set'),
            'add_item_text': self.add_item_text,
            'event': self.event
        }
        context.update(kwargs)
        return context

    def get_success_url(self):
        return reverse('participant-edit', args=(self.object.id,))

    def get(self, request, *args, **kwargs):
        try:
            self.object = Participant.objects.get(event=self.event,
                owner=request.user)
            return HttpResponseRedirect(self.get_success_url())
        except Participant.DoesNotExist:
            return super(ParticipantCreateView, self).get(
                request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None

        participant_form = ParticipantForm(request.POST, prefix='accept')
        formset = self.ModelFormSet(request.POST,
            prefix='participantvideo_set')

        if participant_form.is_valid():
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
                    if instance.nomination not in instance.nominations.all():
                        instance.nominations.clear()
                        vn = VideoNomination(nomination=instance.nomination,
                            participant_video=instance)
                        vn.save()
                return HttpResponseRedirect(self.get_success_url())

        else:
            return self.render_to_response(self.get_context_data(
                formset=formset, participant_form=participant_form))

        return self.render_to_response(self.get_context_data(formset=formset))


class ParticipantUpdateView(ParticipantMixin, OwnerMixin,
    GenericFormsetWithFKUpdateView):
    formset_form_class = ParticipantVideoForm
    template_name = "events/participant_edit_form.html"

    def get_context_data(self, **kwargs):
        context = super(ParticipantUpdateView, self).get_context_data(**kwargs)
        context.update({'event': self.event})
        return context

    def get_queryset(self):
    # Если владелец - текущий пользователь, выбирутся
    # все объекты, иначе ни одного
        return super(ParticipantUpdateView, self).get_queryset().filter(
            Q(owner=self.request.user) | Q(event__owner=self.request.user)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.ModelFormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            object = self.get_object()
            for instance in instances:
                # the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, object)
                instance.save()
                if instance.nomination not in instance.nominations.all():
                    instance.nominations.clear()
                    vn = VideoNomination(nomination=instance.nomination,
                        participant_video=instance)
                    vn.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))


class ParticipantReviewView(ParticipantMixin, GenericFormsetWithFKUpdateView):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoReviewForm
    template_name = 'events/participant_review.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.object = self.get_object()
        self.event = self.object.event
        self.formset_form_class.event = self.event
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class,
            extra=0
        )
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ParticipantReviewView, self).get_context_data(**kwargs)
        context.update({'event': self.event})
        return context

    def get_queryset(self):
    # Если текущий пользователь владелец события, то выбирутся
    # все объекты, иначе ни одного
        return super(ParticipantReviewView, self).get_queryset().filter(
            event__owner=self.request.user
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.ModelFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                instance = form.save(commit=False)
                instance.save()
                print request.POST
                if 'nominations' in form.changed_data:
                    nominations = form.cleaned_data['nominations']
                    currents = instance.nominations.values_list('id', flat=True)
                    removed_nominations = list(set(currents) - set(nominations))
                    added_nominations = list(set(nominations) - set(currents))
                    VideoNomination.objects.filter(
                        nomination__in=removed_nominations).delete()
                    VideoNomination.objects.bulk_create([
                        VideoNomination(nomination=nomination,
                            participant_video=instance)
                        for nomination in added_nominations])
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))


class ParticipantListView(SortingMixin, ListView):
    model = Participant
    paginate_by = 10
    DEFAULT_SORT_FIELD = 'id'
    sort_fields = [
        ('id', u'по дате'),
    ]

    def get_queryset(self):
        return super(ParticipantListView, self).get_queryset().filter(
            event=self.event)

    def get(self, request, *args, **kwargs):
        self.event = Event.objects.get(pk=self.kwargs['event_pk'])
        return super(ParticipantListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ParticipantListView, self).get_context_data(**kwargs)
        ctx['event'] = self.event
        return ctx
