# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Feedback(models.Model):
    subject = models.CharField(max_length=100, verbose_name=_('Subject'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('E-mail'))
    message = models.TextField(verbose_name=_('Message'))
    time = models.DateTimeField(auto_now_add=True, verbose_name=_('Time'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'),
                             null=True, blank=True, default=None)

    class Meta:
        ordering = ['-time']

    def __unicode__(self):
        return self.message

    def save(self, *args, **kwargs):
        super(Feedback, self).save(*args, **kwargs)
        message = u"""
        От {0}
        
        Тема:
        {1}
        
        Сообщение:
        {2}
        """.format(self.name, self.subject, self.message)
        mail = EmailMessage(
            '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, self.subject),
            message, self.email, [a[1] for a in settings.MANAGERS],
            headers={'Reply-To': 'another@example.com'})
        mail.send(fail_silently=True)
