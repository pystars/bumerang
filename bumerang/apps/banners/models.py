# -*- coding: utf-8 -*-
from random import randint

from django.db import models
from django.utils.timezone import now

from bumerang.apps.utils.functions import get_path
from bumerang.apps.utils.models import FileModelMixin, nullable
from bumerang.apps.utils.media_storage import media_storage


class BannerBase(FileModelMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=u'название')
    url = models.URLField(
        verbose_name=u'Ссылка', help_text=u'Заполняется, если баннер не flash',
        **nullable)
    alt = models.CharField(
        max_length=65, verbose_name=u'Описание изображения',
        help_text=u'Заполняется, если баннер не flash', **nullable)
    image = models.ImageField(
        u'изображение', storage=media_storage, upload_to='bs',
        help_text=u'Заполняется, если баннер не flash', **nullable)
    flash = models.FileField(
        u'flash-баннер', storage=media_storage, upload_to='bs',
        help_text=u'заполняется, если это flash-баннер', **nullable)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(u'Дата создания', auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.image:
            return u"""
    <p>
        <a href="{0}">
            <img src="{1}" alt="{2}" width="200" height="340" />
        </a>
    </p>
        """.format(self.url, self.image.url, self.alt)
        return u"""
  <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
   width="200" height="340">
    <param name="movie" value="{0}" />
    <!--[if !IE]>-->
    <object type="application/x-shockwave-flash" data="{0}"
     width="200" height="340">
    <!--<![endif]-->
    <!--[if !IE]>-->
    </object>
    <!--<![endif]-->
  </object>
        """.format(self.flash)


class HeadBanner(FileModelMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Название')
    url = models.URLField(verbose_name=u'Ссылка')
    text = models.CharField(max_length=255, verbose_name=u'Текст ссылки')
    background_image = models.ImageField(
        u'Подложка', storage=media_storage, upload_to='headbs')
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(u'Дата создания', auto_now_add=True)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        verbose_name = u'Баннер в шапке'
        verbose_name_plural = u'Баннеры в шапке'


class MainPageBanner(BannerBase):
    weight = models.IntegerField(u'Вес баннера')

    class Meta:
        verbose_name = u'Баннер главной страницы'
        verbose_name_plural = u'Баннеры главной страницы'

    @classmethod
    def get_some(cls):
        banners = cls.objects.filter(is_active=True)
        if not banners.exists():
            return None
        random_number = randint(1, sum(banner.weight for banner in banners))
        weight = 0
        for banner in banners:
            weight += banner.weight
            if weight > random_number:
                return banner


class EventBanner(BannerBase):
    event = models.ForeignKey('events.Event')

    class Meta:
        verbose_name = u'Баннер события'
        verbose_name_plural = u'Баннеры событий'


class CrossSiteBanner(BannerBase):
    POSITION_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3)
    )
    position = models.IntegerField(u'Позиция', choices=POSITION_CHOICES)

    class Meta:
        verbose_name = u'Сквозной баннер'
        verbose_name_plural = u'Сквозные баннеры'
