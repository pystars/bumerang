# coding=utf-8
from celery.task import task

from bumerang.apps.utils.email import send_new_password, \
    send_activation_success, send_activation_link

@task
def send_new_password_task(new_password, receiver_email):
    send_new_password(new_password, receiver_email)

@task
def send_activation_success_task(receiver_email):
    send_activation_success(receiver_email)

@task
def send_activation_link_task(link, to_addr):
    send_activation_link(link, to_addr)