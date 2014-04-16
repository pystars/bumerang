# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from bumerang.apps.utils.functions import random_string
from bumerang.apps.utils.models import TitleUnicode, nullable, FileModelMixin
from bumerang.apps.utils.media_storage import media_storage
from utils import (
    original_upload_to, image_upload_to, thumbnail_upload_to, icon_upload_to)


class PhotoGenre(models.Model, TitleUnicode):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    class Meta:
        verbose_name = u'Жанр фото'
        verbose_name_plural = u'Жанры фото'
        ordering = ('sort_order', 'title')


class Photo(FileModelMixin, models.Model, TitleUnicode):
    SLUG_LENGTH = 20

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

    slug = models.SlugField(u'Метка', max_length=SLUG_LENGTH, editable=False)
    published_in_archive = models.BooleanField(
        u'Опубликовано в фотогалерее', default=False)
    title = models.CharField(u'Название', max_length=255)
    slug = models.SlugField(u'Метка (часть ссылки)', **nullable)
    original_file = models.ImageField(
        u"Оригинальное фото", upload_to=original_upload_to,
        storage=media_storage, null=True, blank=False)
    image = models.ImageField(
        u"Фото", upload_to=image_upload_to, storage=media_storage, **nullable)
    thumbnail = models.ImageField(
        u"Превью", upload_to=thumbnail_upload_to, storage=media_storage,
        **nullable)
    icon = models.ImageField(
        u"Иконка", upload_to=icon_upload_to, storage=media_storage, **nullable)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=u"Владелец")
    album = models.ForeignKey(
        'albums.PhotoAlbum', verbose_name=u'Альбом', max_length=255, **nullable)
    description = models.TextField(u'Описание', **nullable)
    year = models.IntegerField(u'Год', default=2011, **nullable)
    genre = models.ForeignKey(PhotoGenre, verbose_name=u'Жанр', **nullable)
    country = models.CharField(u'Страна', max_length=255, **nullable)
    city = models.CharField(u'Город', max_length=255, **nullable)
    authors = models.CharField(u'Авторы', max_length=255, **nullable)
    agency = models.CharField(u'учреждение', max_length=255, **nullable)
    teachers = models.CharField(u'Педагоги', max_length=255, **nullable)
    manager = models.CharField(u'Руководитель', max_length=255, **nullable)
    festivals = models.TextField(u'Фестивали', **nullable)
    access = models.IntegerField(
        u'Кому доступно фото', choices=ACCESS_FLAGS_CHOICES,
        default=FREE_FOR_ALL, **nullable)
    created = models.DateTimeField(u'Дата добавления', default=now)
    views_count = models.IntegerField(u'Количество просмотров фото', default=0,
                                      editable=False, **nullable)
    is_processed = models.BooleanField(u'Обработано')

    class Meta:
        verbose_name = u'Фото'
        verbose_name_plural = u'Фото'
        ordering = ('-id',)

    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        if not self.slug:
            self.slug = self.get_slug()

    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        if self.album:
            if not self.album.cover:
                self.album.cover = self
                self.album.save()

    def get_absolute_url(self):
        return reverse('photo-detail', kwargs={'pk': self.pk})

    def get_preview(self):
        if self.image and self.icon:
            return u'<a href="{0}" target="_blank"><img src="{1}"></a>'.format(
                self.image.url, self.icon.url)
        return None
    get_preview.short_description = u'Превью'
    get_preview.allow_tags = True

    @classmethod
    def get_slug(cls):
        while True:
            slug = random_string(cls.SLUG_LENGTH)
            if not cls.objects.filter(slug=slug).exists():
                return slug
