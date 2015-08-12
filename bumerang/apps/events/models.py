# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, pre_save
from django.utils.safestring import mark_safe
from django.db.models.aggregates import Max, Avg
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .signals import (approve_event, winners_public, event_created,
    participant_reviewed, juror_added)
from .notifications import (notify_admins_about_event_request, notify_winners,
    notify_event_owner_about_approve, notify_jurors_about_participant,
    notify_participant_about_review, notify_event_owner_about_participant,
    notify_juror_about_registration, relate_juror_and_profile)
from ..utils.functions import get_path
from ..utils.media_storage import media_storage
from ..utils.models import TitleUnicode, FileModelMixin
from ..video.models import Video


nullable = dict(null=True, blank=True)


def validate_score(value):
    if value < 1:
        raise ValidationError(u'Оценка не может быть меньше единицы')
    if value > 10:
        raise ValidationError(u'Оценка не может быть больше 10')


def get_rules_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return u'event_rules/{0}правила_подачи_заявки_на_{1}{2}'.format(
        instance.pk, instance, ext)


class AdminUrlMixin:

    def admin_url(self):
        return reverse("admin:{0}_{1}_change".format(
            self._meta.app_label, self._meta.model_name), args=(self.pk,))


class Event(FileModelMixin, models.Model):
    CONTEST = 1
    FESTIVAL = 2
    TYPES_CHOICES = (
        (CONTEST, u'Конкурс'),
        (FESTIVAL, u'Фестиваль'),
    )
    parent = models.ForeignKey(
        'self', verbose_name=u'В рамках фестиваля', related_name='contest_set',
        limit_choices_to={'type': FESTIVAL}, on_delete=models.SET_NULL,
        **nullable)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='owned_events')
    type = models.IntegerField(u'Тип события', choices=TYPES_CHOICES)
    is_approved = models.BooleanField(u'Заявка подтверждена', default=False)
    publish_winners = models.BooleanField(
        u'Публиковать победителей', default=False)
    logo = models.ImageField(
        u'Логотип события', upload_to=get_path(u'logos/{0}/full{1}'),
        storage=media_storage, **nullable)
    min_logo = models.ImageField(
        u'Уменьшенный логотип события', upload_to=get_path(u'logos/{0}/min{1}'),
        storage=media_storage, **nullable)

    title = models.CharField(u'Название события', max_length=255)
    opened = models.BooleanField(u'Событие открыто ', default=True)
    start_date = models.DateField(u'Дата начала')
    end_date = models.DateField(u'Дата окончания')
    requesting_till = models.DateField(u'Прием заявок до')
    hold_place = models.TextField(u'Место проведения')
    description = models.TextField(u'Описание события')
    participant_conditions = models.TextField(u'Условия подачи заявок')
    contacts_raw_text = models.TextField(u'Контакты')
    rules_document = models.FileField(
        u'Положение официальный документ', upload_to=get_rules_path,
        storage=media_storage, max_length=255, **nullable)

    created = models.DateTimeField(
        u'Дата добавления', default=now, editable=False)

    jurors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=u'Члены жюри', through='Juror',
        related_name='juror_events')

    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'
        ordering = ('start_date', 'end_date')

    def __unicode__(self):
        title = self.title
        if self.type == self.FESTIVAL:
            year_string = str(self.start_date.year)
            if self.start_date.year != self.end_date.year:
                year_string += '&mdash;{0}'.format(self.end_date.year)
            title += ' {0}'.format(year_string)
        return mark_safe(title)

    def save(self, *args, **kwargs):
        if self.type == self.FESTIVAL:
            self.parent = None
        return super(Event, self).save(*args, **kwargs)

    def chain(self):
        return Event.objects.filter(
            title=self.title,
            owner=self.owner,
            is_approved=True,
            type=self.FESTIVAL)

    def contests(self):
        return self.contest_set.filter(is_approved=True)

    def is_accepting_requests(self):
        if self.requesting_till >= now().date():
            return True
        return False

    def clean_fields(self, exclude=None):
        super(Event, self).clean_fields(exclude)
        if self.type == self.FESTIVAL and self.parent:
            raise ValidationError({
                'parent': [u'Только конкурс может проходить в рамках фестиваля']
            })
        if self.start_date > self.end_date:
            raise ValidationError({
                'end_date': [u'''
                Событие не может закончиться прежде, чем начнется.
                Утром деньги, вечером стулья''']
            })
        if self.requesting_till > self.end_date:
            raise ValidationError({
                'requesting_till': [u'''
                Прием заявок должен заканчиваться до окончания фестиваля''']
            })

    def get_genetive_name(self):
        if self.type == self.CONTEST:
            return u'конкурса'

        if self.type == self.FESTIVAL:
            return u'фестиваля'

        return u'события'

    def get_rules_name(self):
        if self.rules_document:
            return self.rules_document.name.split('/')[1]
        return None

    def owner_name(self):
        return self.owner.get_title()
    owner_name.short_description = u'Имя владельца'

    def banner(self):
        banners = self.eventbanner_set.filter(is_active=True)
        if banners.exists():
            return banners.order_by('-id')[0]
        return None


class Juror(FileModelMixin, models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Событие')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=u'Пользователь')
    email = models.EmailField(_('e-mail address'))
    info_second_name = models.CharField(u'Фамилия', max_length=100)
    info_name = models.CharField(u'Имя', max_length=100)
    info_middle_name = models.CharField(u'Отчество', max_length=100)
    description = models.TextField(u'Описание')
    min_avatar = models.ImageField(
        u'Фото', upload_to=get_path(u'jurors_avatars/{0}/min{1}'), blank=False,
        storage=media_storage, null=True)

    class Meta:
        verbose_name = u'Член жюри'
        verbose_name_plural = u'Члены жюри'
        unique_together = (('event', 'user'),)

    def __unicode__(self):
        return u'{0} {1} {2}'.format(
            self.info_second_name, self.info_name, self.info_middle_name)


class GeneralRule(TitleUnicode, models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Событие')
    title = models.CharField(u'Заголовок', max_length=255)
    description = models.TextField(u'Описание')

    class Meta:
        verbose_name = u'Общие положения'
        verbose_name_plural = u'Общие положения'


class NewsPost(TitleUnicode, models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Событие')
    title = models.CharField(u'Новость', max_length=255)
    description = models.TextField(u'Описание')
    creation_date = models.DateField(
        u'Дата добавления', editable=False, default=now)

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'
        ordering = ('creation_date',)


class Nomination(AdminUrlMixin, models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Фестиваль')
    title = models.CharField(u'Название номинации', max_length=255)
    description = models.CharField(u'Описание', max_length=255, blank=True)
    age_from = models.PositiveSmallIntegerField(
        u'Возраст от (включительно)', **nullable)
    age_to = models.PositiveSmallIntegerField(
        u'Возраст до (включительно)', **nullable)
    sort_order = models.PositiveSmallIntegerField(u'Сортировка')

    class Meta:
        verbose_name = u'Номинация'
        verbose_name_plural = u'Номинации'
        ordering = ('sort_order',)

    def __unicode__(self):
        if self.age_from or self.age_to:
            age_postfix = u' ('
            if self.age_from:
                age_postfix += u'от {0} '.format(self.age_from)
            if self.age_to:
                age_postfix += u'до {0} '.format(self.age_to)
            age_postfix += u'лет)'
        else:
            age_postfix = u' (без возрастных ограничений)'
        return self.title + age_postfix

    def approved(self):
        return self.participantvideo_set.filter(is_accepted=True).distinct()


class Participant(AdminUrlMixin, models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=u'Участник')
    event = models.ForeignKey(Event, verbose_name=u'Событие')
    index_number = models.IntegerField(u'Номер заявки', editable=False)
    is_accepted = models.BooleanField(
        u'Заявка принята', default=False, db_index=True)
    videos = models.ManyToManyField(
        Video, verbose_name=u'Видео', through='ParticipantVideo')

    class Meta:
        unique_together = (
            ('owner', 'event'),
            ('event', 'index_number')
        )
        verbose_name = u'Участник события'
        verbose_name_plural = u'Участники события'

    def __unicode__(self):
        return u'{0} в {1}'.format(self.owner, self.event)

    def save(self, *args, **kwargs):
        if not self.index_number:
            last_index = self.__class__.objects.filter(
                event=self.event).aggregate(
                    Max('index_number'))['index_number__max'] or 0
            self.index_number = last_index + 1
        super(Participant, self).save(*args, **kwargs)


class ParticipantVideo(models.Model):
    score_nums = range(1, 11)

    participant = models.ForeignKey(
        Participant, verbose_name=u'Заявка на фестиваль')
    nomination = models.ForeignKey(
        Nomination, verbose_name=u'Номинация',
        related_name='user_selected_participantvideo_set')
    nominations = models.ManyToManyField(
        Nomination, verbose_name=u'Номинации',
        through='VideoNomination', blank=False)
    age = models.PositiveSmallIntegerField(
        u'Возраст автора', blank=False, help_text=u'(полных лет)')
    video = models.ForeignKey(
        Video, verbose_name=u'Видео', blank=False, on_delete=models.PROTECT)
    is_accepted = models.BooleanField(
        u'Принять видео', default=False, db_index=True)

    class Meta:
        unique_together = (("participant", "video"),)

    def __unicode__(self):
        return u'{0}, {1} лет'.format(self.video, self.age)

    def save(self, *args, **kwargs):
        super(ParticipantVideo, self).save(*args, **kwargs)
        if not self.nominations.exists():
            VideoNomination.objects.create(participant_video=self,
                                           nomination=self.nomination)

    def clean_fields(self, exclude=None):
        super(ParticipantVideo, self).clean_fields(exclude)
        age_from = self.nomination.age_from or 0
        age_to = self.nomination.age_to or 100
        if self.age and not (age_from <= self.age <= age_to):
            raise ValidationError({'age': [u'Возраст автора не подходит']})

    def score(self):
        return self.participantvideoscore_set.aggregate(
            Avg('score'))['score__avg']


class VideoNomination(models.Model):
    WINNER = 1
    SECOND = 2
    THIRD = 3
    STATUS_CHOICES = (
        (WINNER, u'Победитель'),
        (SECOND, u'2 место'),
        (THIRD, u'3 место'),
    )
    participant_video = models.ForeignKey(
        ParticipantVideo, verbose_name=u'Видео участника')
    nomination = models.ForeignKey(Nomination, verbose_name=u'Номинация')
    result = models.PositiveSmallIntegerField(
        u'Итог', choices=STATUS_CHOICES, db_index=True, **nullable)

    def __unicode__(self):
        return u'{0} в номинации {1}'.format(
            self.participant_video, self.nomination)


class ParticipantVideoScore(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=u'Участник')
    participant_video = models.ForeignKey(
        ParticipantVideo, verbose_name=u'Видео участника')
    score = models.SmallIntegerField(u'Оценка', validators=[validate_score])

    class Meta:
        verbose_name = u'Оценка фильма-участника'
        verbose_name_plural = u'Оценки фильмов-участников'


event_created.connect(notify_admins_about_event_request,
                      dispatch_uid='notice_admins_about_event_request')
approve_event.connect(notify_event_owner_about_approve,
                      dispatch_uid='notify_event_owner_about_approve')
winners_public.connect(notify_winners, dispatch_uid='notify_winners')
participant_reviewed.connect(notify_participant_about_review,
                             dispatch_uid='notify_participant_about_review')
participant_reviewed.connect(notify_jurors_about_participant,
                             dispatch_uid='notify_jurors_about_participant')
post_save.connect(notify_event_owner_about_participant, sender=Participant,
                  dispatch_uid='notify_event_owner_about_participant')
pre_save.connect(relate_juror_and_profile, sender=Juror,
                 dispatch_uid='relate_juror_and_profile')
juror_added.connect(notify_juror_about_registration,
                    dispatch_uid='notify_juror_about_registration')
