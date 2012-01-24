# -*- coding: utf-8 -*-
from django.template import loader, Context
#from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives
#from django.template.loader import render_to_string
from django.utils.html import strip_tags
#
#subject, from_email, to = 'Order Confirmation', 'admin@yourdomain.com', 'someone@somewhere.com'
#
#html_content = render_to_string('the_template.html', {'varname':'value'}) # ...
#text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
#
## create the email, and attach the HTML version as well.
#msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#msg.attach_alternative(html_content, "text/html")
#msg.send()

def send_single_email(template, context, subject, from_email, to_list,
                      fail_silently=False):
    tpl = loader.get_template(template)
    ctx = Context(context)
    txt_msg = tpl.render(ctx)
    text_content = strip_tags(txt_msg)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
    msg.attach_alternative(txt_msg, "text/html")
    msg.send()
    #send_mail('Welcome to My Project', t.render(c), 'from@address.com', [new_data['email']], fail_silently=False)

    #send_mail(subject, msg, from_email, to_list, fail_silently)

