# coding=utf-8
from celery.task import task

from apps.utils.email import send_new_password

@task
def send_new_password_task(new_password, receiver_email):
    send_new_password(new_password, receiver_email)