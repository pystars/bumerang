# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.timezone import now

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from bumerang.apps.messages.models import Message


class ComposeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ComposeForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (field.widget.__class__ == forms.widgets.Textarea):
                if field.widget.attrs.has_key('class'):
                    field.widget.attrs['class'] += ' wide'
                else:
                    field.widget.attrs.update({'class': 'wide'})
    """
    A simple default form for private messages.
    """
    recipient = forms.IntegerField(widget=forms.HiddenInput)
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))


    def save(self, sender, parent_msg=None):
        recipient = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
#        for r in recipients:
        Profile = get_user_model()
        msg = Message(
            sender = sender,
            recipient = Profile.objects.get(id=recipient),
            subject = subject,
            body = body,
        )
        if parent_msg is not None:
            msg.parent_msg = parent_msg
            parent_msg.replied_at = now()
            parent_msg.save()
        msg.save()
        message_list.append(msg)
        if notification:
            if parent_msg is not None:
                notification.send([sender], "messages_replied", {'message': msg,})
                notification.send([recipient], "messages_reply_received", {'message': msg,})
            else:
                notification.send([sender], "messages_sent", {'message': msg,})
                notification.send([recipient], "messages_received", {'message': msg,})
        return message_list
