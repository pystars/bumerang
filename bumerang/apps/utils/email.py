# -*- coding: utf-8 -*-
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from bumerang.settings import EMAIL_NOREPLY_ADDR

def send_single_email(template, context, subject, from_email, to_list):
    tpl = loader.get_template(template)
    ctx = Context(context)
    txt_msg = tpl.render(ctx)
    text_content = strip_tags(txt_msg)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
    msg.attach_alternative(txt_msg, "text/html")
    msg.send()


def send_activation_link(link, to_addr):
    ctx = {
        'subject': u'Активация аккаунта на сайте bumerang.tv',
        'header': u'Активация аккаунта на сайте bumerang.tv.',
        'link': link,
    }
    send_single_email("email/activation_email.html", ctx, ctx['subject'],
                      EMAIL_NOREPLY_ADDR, [to_addr])

def send_activation_success(to_addr):
    ctx = {
        'subject': u'Активация на сайте bumerang.tv подтверждена',
        'header': u'Регистрация успешно подтверждена.'
        }
    send_single_email("email/activation_success.html", ctx, ctx['subject'],
                      EMAIL_NOREPLY_ADDR, [to_addr])

def send_new_password(password, to_addr):
    ctx = {
        'subject': u'Восстановление пароля от сервиса bumerang.tv',
        'header': u'Восстановление пароля от сервиса bumerang.tv.',
        'password': password
    }
    send_single_email("email/new_password.html", ctx, ctx['subject'],
                      EMAIL_NOREPLY_ADDR, [to_addr])