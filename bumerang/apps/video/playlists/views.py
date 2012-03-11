# -*- coding: utf-8 -*-
import datetime

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.dates import DateDetailView, _date_from_string

from models import PlayList


class PlaylistDetailView(DateDetailView):
    model = PlayList
    allow_future=True
    date_field = 'rotate_from_date'
    channel = None
    month_format = '%m'

    def get_object(self, queryset=None):
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
            month, self.get_month_format(),
            day, self.get_day_format())

        channel = self.get_channel()

        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_(u"Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
                })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        date_field = self.get_date_field()
        field = qs.model._meta.get_field(date_field)
        lookup = {'%s__lte' % field.name: date}
        lookup.update(channel__slug=channel)
        qs = qs.filter(**lookup).order_by('-{0}'.format(date_field))
        try:
            playlist = qs[0]
        except IndexError:
            raise Http404(u'нет плейлиста для указанных даты и канала')
        playlist.rotate_from_date = date
        return playlist

    def get_channel(self):
        channel = self.channel
        if channel is None:
            try:
                channel = self.kwargs['channel']
            except KeyError:
                try:
                    channel = self.request.GET['channel']
                except KeyError:
                    raise Http404(_(u"No channel specified"))
        return channel
