# -*- coding: utf-8 -*-
# do not touch this import for correct work with avatar
from __future__ import division

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import json
from PIL import Image
from django.db.utils import IntegrityError
from django.forms.models import modelformset_factory
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.forms.util import ErrorList
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext as _

from bumerang.apps.accounts.models import Profile
from bumerang.apps.accounts.views import notify_success, notify_error
from bumerang.apps.events.models import (Event, Nomination, Participant,
    ParticipantVideo, GeneralRule, NewsPost, Juror, VideoNomination,
    ParticipantVideoScore)
from bumerang.apps.events.forms import (EventCreateForm,
    EventUpdateForm, EventLogoEditForm, NominationForm, ParticipantVideoForm,
    GeneralRuleForm, NewsPostForm, JurorForm, ParticipantVideoReviewForm,
    EventContactsUpdateForm, ParticipantForm, ParticipantVideoFormSet,
    SetWinnersForm)
from bumerang.apps.utils.views import (OwnerMixin, SortingMixin,
    GenericFormsetWithFKUpdateView)


class ParticipantMixin(View):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"
    template_name = 'events/participant_form.html'
    formset_extra = 1

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
            self.event = get_object_or_404(Event, id=kwargs['event_pk'])
        else:
            self.object = self.get_object()
            self.event = self.object.event
            queryset = getattr(self.object,
                self.formset_model.__name__.lower() + '_set', None)
            if queryset:
                if queryset.exists():
                    self.formset_extra = 0
        self.formset_form_class.event = self.event
        self.formset_form_class.request = request
        self.ModelFormSet = self.get_model_formset()
        return handler(request, *args, **kwargs)

    def get_model_formset(self):
        return modelformset_factory(self.formset_model, self.formset_form_class,
            extra=self.formset_extra, can_delete=True)


class EventDetailView(DetailView):
    model = Event
    rel_model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            try:
                context['participant'] = Participant.objects.filter(
                    owner=self.request.user,
                    event=context['object']
                )[0]
            except IndexError:
                pass
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


class EventCreateView(CreateView):
    model = Event
    template_name = 'events/event_send_request.html'
    form_class = EventCreateForm

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if self.object.type == Event.FESTIVAL:
            self.object.parent = None
        self.object.save()
        self.template_name = 'events/event_send_request_sended.html'
        return self.render_to_response(self.get_context_data())


class EventPressListView(ListView):
    model = NewsPost

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return event.newspost_set.all().order_by('-pk' ,'-creation_date')

    def get_context_data(self, **kwargs):
        context = super(EventPressListView, self).get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        context.update({
            'event': event,
        })
        return context


class EventFilmsListView(ListView):
    model = ParticipantVideo
    template_name = 'events/films_list.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        if 'nomination_pk' in self.kwargs:
            self.nomination = get_object_or_404(Nomination,
                id=self.kwargs['nomination_pk'], event=self.event)
        else:
            try:
                self.nomination = self.event.nomination_set.all()[0]
            except IndexError:
                self.nomination = None
        return super(EventFilmsListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = ParticipantVideo.objects.filter(is_accepted=True,
            participant__in=self.event.participant_set.all())
        if self.nomination:
            qs = qs.filter(nominations=self.nomination.pk)
        return qs

    def get_context_data(self, **kwargs):
        context = super(EventFilmsListView, self).get_context_data(**kwargs)
        for item in context['object_list']:
            try:
                obj = ParticipantVideoScore.objects.get(
                    owner=self.request.user,
                    participant_video=item
                )
            except ParticipantVideoScore.DoesNotExist:
                obj = None
            item.current_score = obj

        context.update({
            'event': self.event,
            'nomination': self.nomination,
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
    template_name = "events/event_juror_formset.html"
    add_item_text = u'Добавить члена жюри'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.ModelFormSet(request.POST, request.FILES,
            prefix=self.formset_prefix)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.event = self.object
                try:
                    instance.user = User.objects.get(username=instance.email)
                    instance.save()
                except User.DoesNotExist:
                    title = u'{0} {1} {2}'.format(
                        instance.info_second_name,
                        instance.info_name,
                        instance.info_middle_name
                    )
                    profile = Profile(
                        username = instance.email,
                        title = title,
                        info_second_name = instance.info_second_name,
                        info_name = instance.info_name,
                        info_middle_name = instance.info_middle_name
                    )
                    password = User.objects.make_random_password()
                    profile.set_password(password)
                    profile.save()
                    instance.user_id = profile.id
                    instance.save()
                    profile.min_avatar = instance.min_avatar
                    profile.save()
                    #TODO: send letter to new juror with links to password
                    # and event
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))


class EventNewsUpdateView(OwnerMixin, GenericFormsetWithFKUpdateView):
    model = Event
    formset_model = NewsPost
    formset_form_class = NewsPostForm
    template_name = "events/event_edit_formset.html"
    add_item_text = u'Добавить новость'


class EventNewsPostUpdateView(UpdateView):
    model = NewsPost
    form_class = NewsPostForm

    def get_queryset(self):
    # Если владелец события - текущий пользователь, выберутся все новости,
    # иначе ни одного
        return super(EventNewsPostUpdateView, self).get_queryset().filter(
            event__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(EventNewsPostUpdateView, self).get_context_data(**kwargs)
        ctx['event'] = self.object.event
        return ctx

    def get_success_url(self):
        return reverse('event-press', args=(self.object.event.id,))


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
            'formset': self.ModelFormSet(
                prefix='participantvideo_set',
                queryset=self.formset_model.objects.get_empty_query_set()
            ),
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

    def get_model_formset(self):
        return modelformset_factory(self.formset_model, self.formset_form_class,
            formset=ParticipantVideoFormSet, extra=self.formset_extra,
            can_delete=True)


class ParticipantUpdateView(ParticipantMixin, OwnerMixin,
    GenericFormsetWithFKUpdateView):
    formset_form_class = ParticipantVideoForm
    template_name = "events/participant_edit_form.html"

    def get_context_data(self, **kwargs):
        ctx = super(ParticipantUpdateView, self).get_context_data(**kwargs)
        ctx['event'] = self.event
        return ctx

    def get_queryset(self):
    # Если владелец - текущий пользователь, выбирутся
    # все объекты, иначе ни одного
        return super(ParticipantUpdateView, self).get_queryset().filter(
            owner=self.request.user
        )

    def post(self, request, *args, **kwargs):
        formset = self.ModelFormSet(request.POST, prefix=self.formset_prefix)
        if formset.is_valid():
            instances = formset.save(commit=False)
            self.object.is_approved = False
            self.object.save()
            for instance in instances:
                # the name of fk attribute must be same to lower case of fk model
                setattr(instance, self.model_name, self.object)
                instance.is_accepted = False
                instance.save()
                if instance.nomination not in instance.nominations.all():
                    instance.nominations.clear()
                    vn = VideoNomination(nomination=instance.nomination,
                        participant_video=instance)
                    vn.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_model_formset(self):
        return modelformset_factory(self.formset_model, self.formset_form_class,
            formset=ParticipantVideoFormSet, extra=self.formset_extra,
            can_delete=True)


class ParticipantReviewView(ParticipantMixin, GenericFormsetWithFKUpdateView):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoReviewForm
    template_name = 'events/participant_review.html'

    def get_context_data(self, **kwargs):
        context = super(ParticipantReviewView, self).get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_queryset(self):
    # Если текущий пользователь владелец события, то выбирутся
    # все объекты, иначе ни одного
        return super(ParticipantReviewView, self).get_queryset().filter(
            event__owner=self.request.user
        )

    def post(self, request, *args, **kwargs):
        formset = self.ModelFormSet(request.POST, prefix=self.formset_prefix)
        if formset.is_valid():
            self.object.is_accepted = True
            self.object.save()
            for form in formset:
                instance = form.save(commit=False)
                instance.save()
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
        ('is_accepted', u'по состоянию')
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


class ParticipantVideoRatingUpdate(UpdateView):
    model = ParticipantVideo
    response_class = HttpResponse

    def get_object(self, queryset=None):
        self.video = super(
            ParticipantVideoRatingUpdate, self).get_object(queryset)
        kwargs = dict(
            owner=self.request.user,
            participant_video=self.video
        )
        if not ParticipantVideoScore.objects.filter(**kwargs).update(
            score=self.kwargs['rate']):
            obj = ParticipantVideoScore(score=self.kwargs['rate'], **kwargs)
            obj.save()
        else:
            obj = ParticipantVideoScore.objects.get(**kwargs)
        return obj

    def render_to_response(self, context, **response_kwargs):
        response = {
            'average': self.video.get_average_score(),
            'current': context['object'].score,
            'object_id': self.video.id
        }
        json = JSONEncoder().encode(response)
        return HttpResponse(json, mimetype="application/json")


class EventConditionsDetailView(DetailView):
    model = Event
    template_name = 'events/event_request_conditions.html'


class SetWinnersView(UpdateView):
    model = VideoNomination
    form_class = SetWinnersForm

    def get_queryset(self):
        return super(SetWinnersView, self).get_object(queryset).filter(
            participant_video = self.kwargs['participant_video'],
            nomination = self.kwargs['nomination'],
            nomination__event__owner = self.request.user
        )

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        try:
            obj = queryset.get()
        except self.model.DoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                      {'verbose_name': queryset.model._meta.verbose_name})

        return obj

    def form_valid(self, form):
        return self.render_to_response({'success': True})

    def form_invalid(self, form):
        return self.render_to_response({'success': False})

    def render_to_response(self, context, **response_kwargs):
        json = JSONEncoder().encode(context)
        return HttpResponse(json, mimetype="application/json")
