# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from mptt.models import MPTTModel, TreeForeignKey


class Advice(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    description = models.TextField(verbose_name=u'Описание раздела', default=u'Введите описание')
    # Slug of node's name
    slug = models.SlugField()
    # Url hash
    url = models.CharField(max_length=1024, editable=False)
    sort_order = models.IntegerField(default=0, verbose_name=u'Позиция')
    
    def get_absolute_url(self):
        return '/advices/%s/' % self.url

    def __unicode__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
        ordering = ['level', 'sort_order', 'id']

    class Meta:
        verbose_name = u'Совет'
        verbose_name_plural = u'Советы'
        ordering = ['level', 'sort_order', 'id']

@receiver(pre_save, sender=Advice)
def advice_pre_save(sender, **kwargs):
    advice = kwargs['instance']
    # Building advice URL from parents
    url = ''.join([ancestor.slug + u'/' for ancestor in advice.get_ancestors(ascending=False)] + [advice.slug])
    advice.url = url
