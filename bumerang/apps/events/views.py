# -*- coding: utf-8 -*-
# do not touch this import for correct work with avatar
from __future__ import division
import json
from datetime import datetime
from cStringIO import StringIO

from PIL import Image
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.db.models.aggregates import Avg
from django.db.models.query_utils import Q
from django.http import (
    HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden)
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.views.generic import (
    View, CreateView, UpdateView, ListView, DetailView)
from django.contrib.auth import get_user_model

from bumerang.apps.utils.views import (
    OwnerMixin, SortingMixin, GenericFormsetWithFKUpdateView)
from bumerang.apps.accounts.views import notify_success, notify_error
from bumerang.apps.accounts.forms import (
    UserContactsForm, OrganizationContactsForm)
from bumerang.apps.events.models import (
    ParticipantVideo, GeneralRule, NewsPost, Juror, VideoNomination,
    ParticipantVideoScore, Event, Nomination, Participant)
from bumerang.apps.events.forms import (
    EventUpdateForm, EventLogoEditForm, NominationForm, ParticipantVideoForm,
    GeneralRuleForm, NewsPostForm, JurorForm, ParticipantVideoReviewForm,
    EventContactsUpdateForm, ParticipantForm, ParticipantVideoFormSet,
    SetWinnersForm, EventCreateForm)
from .signals import event_created, winners_public,  participant_reviewed


Profile = get_user_model()


class ParticipantMixin(View):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"
    template_name = 'events/participant_form.html'
    formset_extra = 1

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed)
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
        return modelformset_factory(
            self.formset_model, self.formset_form_class,
            extra=self.formset_extra, can_delete=True)


class EventDetailView(DetailView):
    model = Event
    rel_model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoForm
    add_item_text = u"Добавить еще одну работу"

    def get_context_data(self, **kwargs):
        kwargs['profile'] = self.object.owner
        if self.request.user.is_authenticated():
            qs = Participant.objects.filter(
                owner=self.request.user, event=self.object)
            if qs.exists():
                kwargs['participant'] = qs[0]
            kwargs.update({
                'participant_form': ParticipantForm(
                    prefix='accept', initial={'accepted': False}),
                'formset': self.ModelFormSet(
                    prefix='participantvideo_set',
                    queryset=ParticipantVideo.objects.none()),
                'add_item_text': self.add_item_text,
            })
        return super(EventDetailView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_approved and self.object.owner != request.user:
            return Http404()
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
    DEFAULT_SORT_FIELD = 'created'
    DEFAULT_SORT_DIRECTION = 'desc'
    sort_fields = [
        ('created', u'по умолчанию'),
        ('requesting_till', u'Прием заявок открыт')
    ]

    def get_filter(self):
        result = {}
        if self.sort_field == 'requesting_till':
            result['requesting_till__gte'] = now().date()
        if 'type' in self.kwargs:
            result['type'] = self.kwargs['type']
        return result

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
        self.object.save()
        event_created.send(self, event=self.object)
        self.template_name = 'events/event_send_request_sended.html'
        return self.render_to_response(self.get_context_data())


class EventPressListView(ListView):
    model = NewsPost

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return event.newspost_set.all().order_by('-pk', '-creation_date')

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
            self.nomination = get_object_or_404(
                Nomination, id=self.kwargs['nomination_pk'], event=self.event)
        else:
            try:
                self.nomination = self.event.nomination_set.all()[0]
            except IndexError:
                self.nomination = None
        return super(EventFilmsListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = ParticipantVideo.objects.filter(
            is_accepted=True, participant__in=self.event.participant_set.all())
        if self.nomination:
            qs = qs.filter(nominations=self.nomination.pk)
        qs = qs.annotate(average_score=Avg('participantvideoscore__score'))
        return qs

    def get_context_data(self, **kwargs):
        context = super(EventFilmsListView, self).get_context_data(**kwargs)
        winners = {}
        if self.nomination and (
                self.event.publish_winners or
                    self.event.owner is self.request.user):
            fields = ('participant_video', 'result')
            winners = dict(self.nomination.videonomination_set.filter(
                result__isnull=False).values_list(*fields))
        for item in context['object_list']:
            if self.request.user in self.event.jurors.all():
                try:
                    item.current_score = ParticipantVideoScore.objects.get(
                        owner=self.request.user,
                        participant_video=item
                    )
                except ParticipantVideoScore.DoesNotExist:
                    item.current_score = None
            if item.id in winners.keys():
                item.result = winners[item.id]
        context.update({
            'event': self.event,
            'nomination': self.nomination,
        })
        return context


class EventWinnersListView(ListView):
    model = VideoNomination
    template_name = 'events/event_winners_list.html'

    def get(self, request, *args, **kwargs):
        qs = Event.objects.filter(pk=self.kwargs.get('event_pk'))
        if request.user.is_authenticated():
            qs = qs.filter(Q(publish_winners=True) | Q(owner=request.user))
        else:
            qs = qs.filter(publish_winners=True)
        try:
            self.event = qs.get()
        except Event.DoesNotExist:
            raise Http404(u"Страница не найдена")
        return super(EventWinnersListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return VideoNomination.objects.filter(
            nomination__event=self.event,
            result__isnull=False).select_related(
                'participant_video', 'participant_video__video'
            ).annotate(
                average_score=Avg(
                    'participant_video__participantvideoscore__score')
            ).order_by('nomination__sort_order')

    def get_context_data(self, **kwargs):
        context = super(EventWinnersListView, self).get_context_data(**kwargs)
        context.update({
            'event': self.event,
        })
        return context


class EventEditInfoView(OwnerMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm

    def get_success_url(self):
        return reverse('event-edit-info', kwargs={'pk': self.object.pk})


class EventEditLogoView(OwnerMixin, UpdateView):
    model = Event
    form_class = EventLogoEditForm
    template_name = "events/event_edit_logo.html"

    def get_success_url(self):
        return reverse('event-edit-logo', kwargs={'pk': self.object.pk})

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

        suf = SimpleUploadedFile(
            'min.jpg', temp_handle.read(), content_type='image/jpg')

        self.object.min_logo.save('min.jpg', suf, save=False)
        form.save()

        notify_success(self.request, message=u'Логотип успешно обновлен.')

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
        formset = self.ModelFormSet(
            request.POST, request.FILES, prefix=self.formset_prefix)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                if Juror.objects.filter(
                        event=self.object, user__email=instance.email).exists():
                    continue
                instance.event = self.object
                # we have a signal which calls on pre_save for Juror in models
                instance.save()
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
        return reverse('event-edit-contacts', kwargs={'pk': self.object.pk})


class ContactsCheckMixin:
    def get_no_filled_fields(self, request):
        if request.user.type == Profile.TYPE_USER:
            form = UserContactsForm()
        else:
            form = OrganizationContactsForm()
        required_field_names = [
            name for name, field in form.fields.iteritems() if field.required]
        profile = request.user
        result = []
        for field_name in required_field_names:
            if not getattr(profile, field_name):
                result.append(Profile._meta.get_field(field_name).verbose_name)
        return result


class ParticipantCreateView(ParticipantMixin, CreateView, ContactsCheckMixin):

    def get_context_data(self, **kwargs):
        context = {
            'participant_form': ParticipantForm(
                prefix='accept', initial={'accepted': False}),
            'formset': self.ModelFormSet(
                prefix='participantvideo_set',
                queryset=self.formset_model.objects.none()
            ),
            'add_item_text': self.add_item_text,
            'event': self.event,
            'no_filled_fields': self.get_no_filled_fields(self.request)
        }
        context.update(kwargs)
        return context

    def get_success_url(self):
        return reverse('participant-confirm', args=(self.object.id,))

    def get(self, request, *args, **kwargs):
        try:
            self.object = Participant.objects.get(
                event=self.event, owner=request.user)
            return HttpResponseRedirect(self.get_success_url())
        except Participant.DoesNotExist:
            return super(ParticipantCreateView, self).get(
                request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.event.is_accepting_requests():
            raise Http404(u'Страница не найдена')
        self.object = None
        participant_form = ParticipantForm(request.POST, prefix='accept')
        formset = self.ModelFormSet(request.POST, prefix='participantvideo_set')

        if participant_form.is_valid():
            if (formset.is_valid() and
                    (formset.total_form_count() > len(formset.deleted_forms))):
                self.object = self.model(owner=request.user, event=self.event)
                try:
                    self.object.save()
                except IntegrityError:
                    try:
                        # in case of already exist participant
                        self.object = self.model.objects.get(
                            event=self.event, owner=request.user)
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
                        vn = VideoNomination(
                            nomination=instance.nomination,
                            participant_video=instance)
                        vn.save()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                formset=formset, participant_form=participant_form))

        return self.render_to_response(self.get_context_data(formset=formset))

    def get_model_formset(self):
        return modelformset_factory(
            self.formset_model, self.formset_form_class,
            formset=ParticipantVideoFormSet, extra=self.formset_extra,
            can_delete=True)


class ParticipantConfirmView(ParticipantMixin, OwnerMixin, DetailView):
    template_name = "events/participant_confirm.html"

    def get_context_data(self, **kwargs):
        ctx = super(ParticipantConfirmView, self).get_context_data(**kwargs)
        ctx['event'] = self.event
        return ctx


class ParticipantPrintView(ParticipantMixin, DetailView):
    template_name = "events/participant_print.html"

    def get_queryset(self):
        return super(ParticipantPrintView, self).get_queryset().filter(
            event__owner=self.request.user)


class ParticipantUpdateView(ParticipantMixin, OwnerMixin, ContactsCheckMixin,
                            GenericFormsetWithFKUpdateView):
    formset_form_class = ParticipantVideoForm
    template_name = "events/participant_edit_form.html"

    def get_context_data(self, **kwargs):
        ctx = super(ParticipantUpdateView, self).get_context_data(**kwargs)
        ctx['event'] = self.event
        ctx['no_filled_fields'] = self.get_no_filled_fields(self.request)
        return ctx

    def get_success_url(self):
        return reverse('participant-confirm', args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        if not self.event.is_accepting_requests():
            raise Http404(u'Страница не найдена')
        formset = self.ModelFormSet(request.POST, prefix=self.formset_prefix)
        if formset.is_valid():
            if formset.total_form_count() <= len(formset.deleted_forms):
                self.object.delete()
                return HttpResponseRedirect(
                    reverse('event-detail', args=(self.event.id,)))
            instances = formset.save(commit=False)
            self.object.is_accepted = False
            self.object.save()
            for instance in instances:
                # the name of fk attribute should be lower case of fk model
                setattr(instance, self.model_name, self.object)
                instance.is_accepted = False
                instance.save()
                if instance.nomination not in instance.nominations.all():
                    instance.nominations.clear()
                    vn = VideoNomination(
                        nomination=instance.nomination,
                        participant_video=instance)
                    vn.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_model_formset(self):
        return modelformset_factory(
            self.formset_model, self.formset_form_class,
            formset=ParticipantVideoFormSet, extra=self.formset_extra,
            can_delete=True)


class ParticipantReviewView(ParticipantMixin, GenericFormsetWithFKUpdateView):
    model = Participant
    formset_model = ParticipantVideo
    formset_form_class = ParticipantVideoReviewForm
    template_name = 'events/participant_review.html'

    def __init__(self, **kwargs):
        super(ParticipantReviewView, self).__init__(**kwargs)
        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.formset_form_class
        )

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
                    nominations = [nomination.id for nomination
                                   in form.cleaned_data['nominations']]
                    currents = instance.nominations.values_list(
                        'id', flat=True)
                    removed_nominations = list(
                        set(currents) - set(nominations))
                    added_nominations = list(
                        set(nominations) - set(currents))
                    VideoNomination.objects.filter(
                        participant_video=instance,
                        nomination__in=removed_nominations).delete()
                    VideoNomination.objects.bulk_create([
                        VideoNomination(
                            nomination_id=nomination,
                            participant_video=instance)
                        for nomination in added_nominations])
            notify_success(request, u'Данные сохранены')
            participant_reviewed.send(self, participant=self.object)
            return HttpResponseRedirect(self.get_success_url())
        notify_error(request, u'При сохранении произошла ошибка')
        return self.render_to_response(self.get_context_data(
            form=self.get_form(self.get_form_class()), formset=formset))

    def get_model_formset(self):
        return modelformset_factory(self.formset_model,
                                    self.formset_form_class,
                                    extra=self.formset_extra)


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

    def set_rating(self):
        kwargs = dict(owner=self.request.user, participant_video=self.object)
        if not ParticipantVideoScore.objects.filter(**kwargs).update(
                score=self.kwargs['rate']):
            ParticipantVideoScore.objects.create(
                score=self.kwargs['rate'], **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.request.user not in self.object.participant.event.jurors.all():
            return HttpResponseForbidden("You're not juror of this event")
        self.set_rating()
        response = {
            'average': self.object.participantvideoscore_set.all().aggregate(
                Avg('score'))['score__avg'] or 0,
            'current': self.kwargs['rate'],
            'object_id': self.object.pk
        }
        return HttpResponse(
            json.JSONEncoder().encode(response), mimetype="application/json")


class EventConditionsDetailView(DetailView):
    model = Event
    template_name = 'events/event_request_conditions.html'


class SetWinnersView(UpdateView):
    model = VideoNomination
    form_class = SetWinnersForm

    def get_queryset(self):
        return super(SetWinnersView, self).get_queryset().filter(
            participant_video=self.kwargs['participant_video'],
            nomination=self.kwargs['nomination'],
            nomination__event__owner=self.request.user
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
        self.object = form.save()
        return self.render_to_response({'success': True})

    def form_invalid(self, form):
        return self.render_to_response({'success': False})

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(
            json.JSONEncoder().encode(context), mimetype="application/json")


class EventPublishWinners(OwnerMixin, DetailView):
    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.publish_winners = True
        self.object.save()
        winners_public.send(self, event=self.object)
        return HttpResponseRedirect(reverse(
            'event-winners-list', args=(self.object.pk,)))


class ParticipantListCSVView(ListView):
    model = ParticipantVideo
    template_name_suffix = '_csv'

    def get_queryset(self):
        return super(ParticipantListCSVView, self).get_queryset().filter(
            participant__event=self.event,
            participant__event__owner=self.request.user
        ).select_related(
        ).annotate(average_score=Avg('participantvideoscore__score'))

    def get(self, request, *args, **kwargs):
        self.event = Event.objects.get(pk=self.kwargs['event_pk'])
        return super(ParticipantListCSVView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ParticipantListCSVView, self).get_context_data(**kwargs)
        ctx['event'] = self.event
        return ctx

    def render_to_response(self, context, **response_kwargs):
        return super(ParticipantListCSVView, self).render_to_response(
            context, mimetype="application/vnd.ms-excel")


class EventScoreCardView(DetailView):
    model = Event
    template_name_suffix = '_scorecard'

    def get_queryset(self):
        return super(EventScoreCardView, self).get_queryset().filter(
            owner=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        return super(EventScoreCardView, self).render_to_response(
            context, mimetype="application/vnd.ms-excel")


class EventFinalStatement(EventScoreCardView):
    template_name_suffix = '_final_statement'
