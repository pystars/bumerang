# -*- coding: utf-8 -*-
from __future__ import division
import json

from PIL import Image

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
from django.forms.util import ErrorList
from django.forms.models import modelformset_factory
from django.views.generic import ListView, UpdateView, View, TemplateView, CreateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import DetailView
from bumerang.apps.accounts.models import Profile
from bumerang.apps.accounts.views import notify_success, notify_error
from bumerang.apps.festivals.forms import FestivalGroupForm, FestivalForm, \
    FestivalLogoEditForm, FestivalNominationForm, FestivalRequestForm

from bumerang.apps.festivals.models import Festival, FestivalNomination, FestivalRequest


class FestivalListView(ListView):
    model = Festival
    paginate_by = 10

    def get_queryset(self):
        qs = super(FestivalListView, self).get_queryset()
        # hidden fest conditions will be here
        qs = qs.filter(
            opened=True,
        )

        return qs


class FestivalEditMixin(UpdateView):
    model = Festival

    def _get_profile(self, request):
        try:
            return request.user.profile
        except ObjectDoesNotExist:
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


class FestivalSendRequest(TemplateResponseMixin, View):
    template_name = 'festivals/festival_send_request.html'
    group_form_class = FestivalGroupForm
    fest_form_class = FestivalForm

    def get_context_data(self, **kwargs):
        ctx = dict()
        ctx.update({
            'profile': self.request.user.profile,
            'group_form': self.group_form_class(prefix='group'),
            'fest_form': self.fest_form_class(prefix='fest'),
        })
        ctx.update(kwargs)
        return ctx

    def get(self, request, *args, **kwargs):

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        group_form = self.group_form_class(request.POST)
        fest_form = self.fest_form_class(request.POST)

        if group_form.is_valid() and fest_form.is_valid():
            owner = Profile.objects.get(id=request.user.id)
            group = group_form.save(commit=False)
            group.owner = owner
            group.save()
            festival = fest_form.save(commit=False)
            festival.owner = owner
            festival.group = group
            festival.save()

            self.template_name = \
                'festivals/festival_send_request_sended.html'
            return self.render_to_response(self.get_context_data())

        else:
            return self.render_to_response(self.get_context_data(
                group_form=group_form,
                fest_form=fest_form
            ))


class FestivalDetailView(DetailView):
    model = Festival

    def get_context_data(self, **kwargs):
        context = kwargs

        group = self.get_object().group

        festivals_archive = Festival.objects.filter(
            group=group
        ).order_by('start_date')

        context.update({
            'festivals_group_name': group.name,
            'festivals_archive': festivals_archive,
        })

        return context

class FestivalEditInfoView(FestivalEditMixin, UpdateView):
    model = Festival
    form_class = FestivalForm

    def get_success_url(self):
        return reverse(
            'festival-edit-info',
            kwargs = { 'pk': self.object.pk },
        )


class FestivalEditLogoView(FestivalEditMixin, UpdateView):
    model = Festival
    form_class = FestivalLogoEditForm
    template_name = "festivals/festivals_edit_logo.html"

    def get_success_url(self):
        return reverse(
            'festival-edit-logo',
            kwargs = {'pk': self.object.pk},
        )

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


class FestivalFormsetGenericView(UpdateView):
    model = None
    formset_model = None
    form_class = None
    add_item_text = None

    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)

        self.ModelFormSet = modelformset_factory(
            model=self.formset_model,
            form=self.form_class,
            can_delete=True
        )

    def _get_profile(self, request):
        try:
            return request.user.profile
        except ObjectDoesNotExist:
            return Profile()

    def get_object(self, queryset=None):
        obj = super(FestivalFormsetGenericView, self).get_object()
        if obj.owner != self._get_profile(self.request):
            raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = kwargs

        festival = self.get_object()

        qs = self.formset_model.objects.filter(
            festival=festival
        )

        context.update({
            'profile': self._get_profile(self.request),
            'festival': festival,
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
            festival = self.get_object()
            for instance in instances:
                instance.festival = festival
                instance.save()

            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(formset=formset))


#class FestivalFormsetRequestView(FestivalFormsetGenericView):
#
#    def post(self, request, *args, **kwargs):
#        formset = self.ModelFormSet(request.POST, request.FILES)
#
#        if formset.is_valid():
#            instances = formset.save(commit=False)
#            festival = self.get_object()
#            submitter = self._get_profile(request)
#
#            for instance in instances:
#                instance.festival = festival
#                instance.submitter = submitter
#                instance.save()
#
#            return HttpResponseRedirect(self.get_success_url())
#
#        return self.render_to_response(self.get_context_data(formset=formset))


class FestivalRequestFormView(CreateView):
    model = FestivalRequest
    form_class = FestivalRequestForm
    template_name = 'festivals/festival_request_form.html'

    def get_context_data(self, **kwargs):
        context = super(FestivalRequestFormView, self).get_context_data(**kwargs)
        festival = Festival.objects.get(id=self.kwargs['pk'])

        context.update({
            'festival': festival
        })

        return context