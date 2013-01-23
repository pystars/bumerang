# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey


class Advice(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    description = models.TextField(
        u'Описание раздела', default=u'Введите описание')
    # Slug of node's name
    slug = models.SlugField()
    # Url hash
    url = models.CharField(max_length=1024, editable=False)
    # TODO: remove sort_order field
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')

    def get_absolute_url(self):
        return '/advices/%s/' % self.url

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name, verbose_name_plural = u'Совет', u'Советы'


@receiver(pre_save, sender=Advice)
def advice_pre_save(sender, **kwargs):
    advice = kwargs['instance']
    # Building advice URL from parents
    advice.url = u'/'.join(advice.get_ancestors(
        include_self=True).values_list('slug', flat=True))
