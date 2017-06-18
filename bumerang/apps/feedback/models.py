# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseFeedback(models.Model):
    type = models.CharField(choices=settings.FEEDBACK_CHOICES, max_length=100,
                            verbose_name=_('Type'))
    message = models.TextField(verbose_name=_('Message'))
    time = models.DateTimeField(auto_now_add=True, verbose_name=_('Time'))

    class Meta:
        abstract = True
        ordering = ['-time']

    def __unicode__(self):
        return self.message

    def save(self, *args, **kwargs):
        super(BaseFeedback, self).save(*args, **kwargs)
        url_pattern = 'admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name)
        url = reverse(url_pattern, args=(self.id,))
        mail_managers(
            u'Новое сообщение с сайта probumerang.tv',
            u'Смотрите раздел feedback в админ-панели probumerang.tv',
            fail_silently=True,
            html_message=u'<a href="{0}">Посмотреть сообщение</a>'.format(url)
        )


class Feedback(BaseFeedback):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))

    def get_absolute_url(self):
        return reverse('admin:view-feedback', args=[self.id])


class AnonymousFeedback(BaseFeedback):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'),
                             null=True, blank=True, default=None)

    def get_absolute_url(self):
        return reverse('admin:view-anon-feedback', args=[self.id])
