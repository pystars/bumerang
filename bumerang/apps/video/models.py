# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.deletion import ProtectedError
from django.utils.timezone import now
from djangoratings import RatingField

from bumerang.apps.utils.functions import random_string
from bumerang.apps.utils.models import TitleUnicode, nullable, FileModelMixin
from bumerang.apps.utils.media_storage import media_storage
from bumerang.apps.video.validators import is_video_file
from utils import (original_upload_to, hq_upload_to, screenshot_upload_to,
                   thumbnail_upload_to, icon_upload_to)


class VideoCategory(models.Model, TitleUnicode):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    class Meta:
        verbose_name = u'Категория видео'
        verbose_name_plural = u'Категории видео'
        ordering = ('sort_order', 'title')


class VideoGenre(models.Model, TitleUnicode):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    class Meta:
        verbose_name = u'Жанр видео'
        verbose_name_plural = u'Жанры видео'
        ordering = ('sort_order', 'title')


class Video(models.Model, TitleUnicode):
    SLUG_LENGTH = 12

    FREE_FOR_ALL = 1
    ACCESS_URL = 2
    ACCESS_PASSWORD = 3
    ACCESS_FRIENDS = 4
    FOR_ME_ONLY = 5
    ACCESS_FLAGS_CHOICES = (
        (FREE_FOR_ALL, u'Всем пользователям'),
        (ACCESS_URL, u'Пользователем, у которых есть ссылка'),
        (ACCESS_PASSWORD, u'Пользователем, у которых есть ссылка и пароль'),
        (ACCESS_FRIENDS, u'Друзьям'),
        (FOR_ME_ONLY, u'Только мне'),
    )

    PENDING = 0
    CONVERTING = 1
    READY = 2
    ERROR = 3
    STATUS_CHOICES = (
        (PENDING, u'видео не загружено'),
        (CONVERTING, u'конвертируется'),
        (READY, u'обработано'),
        (ERROR, u'ошибка обработки')
    )

    published_in_archive = models.BooleanField(
        u'ОВ', default=False, help_text=u'Опубликовано в архиве')
    is_in_broadcast_lists = models.BooleanField(
        u'СВ', default=False, help_text=u'В списках вещания')
    title = models.CharField(u'Название', max_length=255)
    slug = models.SlugField(
        u'Метка (часть ссылки)', max_length=SLUG_LENGTH, editable=False,
        **nullable)
    original_file = models.FileField(
        u"Оригинальное видео", validators=[is_video_file],
        upload_to=original_upload_to, storage=media_storage, **nullable)
    hq_file = models.FileField(
        u'Видео высокого качества', upload_to=hq_upload_to,
        storage=media_storage, validators=[is_video_file],
        help_text=u'В это поле можно загружать ТОЛЬКО готовое, '
                  u'сконвертированное видео в формате mp4. Если вы не знаете о '
                  u'чем идет речь воспользуйтесь полем для загрузки видео на '
                  u'конвертацию', **nullable)
#    mq_file = models.FileField(u'Видео среднего качества',
#        upload_to=mq_upload_to,storage=media_storage,
#        validators=[is_video_file], **nullable)
#    lq_file = models.FileField(u'Видео низкого качества',
#        upload_to=lq_upload_to,storage=media_storage,
#        validators=[is_video_file], **nullable)
    duration = models.IntegerField(
        u'Длительность', default=0, editable=False, **nullable)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=u"Владелец")
    album = models.ForeignKey(
        'albums.VideoAlbum', verbose_name=u'Альбом', max_length=255, **nullable)
    category = models.ForeignKey(
        VideoCategory, verbose_name=u'Категория', **nullable)
    description = models.TextField(u'Описание', **nullable)
    year = models.IntegerField(u'Год', default=2012, **nullable)
    genre = models.ForeignKey(VideoGenre, verbose_name=u'Жанр', **nullable)
    country = models.CharField(u'Страна', max_length=255, **nullable)
    city = models.CharField(u'Город', max_length=255, **nullable)
    authors = models.CharField(u'Авторы', max_length=255, **nullable)
    agency = models.CharField(u'учреждение', max_length=255, **nullable)
    teachers = models.CharField(u'Педагоги', max_length=255, **nullable)
    manager = models.CharField(u'Руководитель', max_length=255, **nullable)
    festivals = models.TextField(u'Фестивали', **nullable)
    access = models.IntegerField(
        u'Кому доступно видео', choices=ACCESS_FLAGS_CHOICES,
        default=FREE_FOR_ALL, **nullable)
    created = models.DateTimeField(u'Дата добавления', default=now)
    views_count = models.IntegerField(
        u'Количество просмотров видео', default=0, editable=False, **nullable)
    status = models.IntegerField(
        u'статус', choices=STATUS_CHOICES, default=PENDING)

    rating = RatingField(range=10, can_change_vote=True)

    class Meta:
        verbose_name = u'Видео'
        verbose_name_plural = u'Видео'
        ordering = ('-id',)

    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        if not self.slug:
            self.slug = self.get_slug()

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)
        if self.album:
            if not self.album.preview and self.preview():
                self.album.preview = self.preview()
                self.album.save()

    def preview(self):
        try:
            return self.preview_set.all()[0]
        except IndexError:
            return None

    def best_quality_file(self):
#        return self.hq_file or self.mq_file or self.lq_file or None
        return self.hq_file

    def any_file(self):
        return self.best_quality_file() or self.original_file or None

    def seconds_duration(self):
        return (self.duration or 0) / 1000

    @classmethod
    def get_slug(cls):
        while True:
            slug = random_string(cls.SLUG_LENGTH)
            if not cls.objects.filter(slug=slug).exists():
                return slug

    def rtmp_url(self):
        return settings.RTMP_SERVER_FORMAT.format(self.best_quality_file().name)

    def delete(self, *args, **kwargs):
        try:
            super(Video, self).delete(*args, **kwargs)
            s3bucket = self.original_file.storage.bucket
            s3bucket.delete_keys(
                s3bucket.get_all_keys(prefix='videos/{0}'.format(self.slug)),
                True
            )
        except ProtectedError:
            #TODO: notice user about it
            pass

        except AttributeError:
            # so, we have not S3 :(
            pass

    def is_protected(self):
        return (self.participantvideo_set.exists()
                or self.playlistitem_set.exists())

    def get_absolute_url(self):
        return u'<a target="_blank" href="{0}">посмотреть</a>'.format(
            reverse('video-detail', args=(self.id,)))
    get_absolute_url.short_description = u'Ссылка'
    get_absolute_url.allow_tags = True

    def get_download_original_file(self):
        if self.original_file:
            return u'<a target="_blank" href="{0}">скачать оригинал</a>'.format(
                self.original_file.url)
        return u'нету пока'
    get_download_original_file.short_description = u'Ссылка на оригинал'
    get_download_original_file.allow_tags = True


class Preview(FileModelMixin, models.Model):
    owner = models.ForeignKey(Video)
    image = models.ImageField(
        upload_to=screenshot_upload_to, storage=media_storage)
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_to, storage=media_storage)
    icon = models.ImageField(upload_to=icon_upload_to, storage=media_storage)
