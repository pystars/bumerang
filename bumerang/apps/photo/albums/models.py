# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Max
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.contrib.auth.models import User

from bumerang.apps.utils.models import TitleUnicode, nullable
from bumerang.apps.photo.models import Photo


class PhotoCategory(models.Model, TitleUnicode):
    title = models.CharField(max_length=255, verbose_name=u"Имя")
    slug = models.SlugField()
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    class Meta:
        verbose_name = u'Категория фото'
        verbose_name_plural = u'Категории фото'
        ordering = ('sort_order', 'title')


class PhotoAlbum(models.Model, TitleUnicode):
    owner = models.ForeignKey(User)
    published_in_archive = models.BooleanField(
        u'Опубликовано в фотогалерее', default=False)
    title = models.CharField(u'Название', max_length=100)
    description = models.TextField(u'Описание', **nullable)
    cover = models.ForeignKey(Photo, on_delete=models.SET_NULL, **nullable)
    category = models.ForeignKey(
        PhotoCategory, verbose_name=u'Категория', **nullable)
    created = models.DateTimeField(u'Дата добавления', default=now)

    class Meta:
        verbose_name = u'Фотоальбом'
        verbose_name_plural = u'Фотоальбомы'

    def get_absolute_url(self):
        return reverse('photo-album-detail', args=(self.id,))
    get_absolute_url.short_description = u'Ссылка на страницу фотоальбома'

    def get_owner_profile(self):
        return self.owner.profile
    get_owner_profile.short_description = u'Имя владельца'

    def last_update(self):
        return self.photo_set.all().aggregate(Max('created'))['created__max']
    last_update.short_description = u'Последнее фото добавлено'

    def preview(self):
        if self.cover:
            return self.cover
        return None
