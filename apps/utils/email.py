# -*- coding: utf-8 -*-
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def send_single_email(template, context, subject, from_email, to_list):
    tpl = loader.get_template(template)
    ctx = Context(context)
    txt_msg = tpl.render(ctx)
    text_content = strip_tags(txt_msg)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
    msg.attach_alternative(txt_msg, "text/html")
    msg.send()


