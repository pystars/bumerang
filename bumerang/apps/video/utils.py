# -*- coding: utf-8 -*-
import os

def original_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'videos/{0}/original{1}'.format(instance.slug, ext)

def hq_upload_to(instance, filename):
    return 'videos/{0}/hq_file.mp4'.format(instance.slug)

#def mq_upload_to(instance, filename):
#    return 'videos/{0}/mq_file.mp4'.format(instance.slug)
#
#def lq_upload_to(instance, filename):
#    return 'videos/{0}/lq_file.mp4'.format(instance.slug)

def screenshot_upload_to(instance, filename):
    return 'videos/{0}/screenshots/{1}'.format(instance.owner.slug, filename)

def thumbnail_upload_to(instance, filename):
    return 'videos/{0}/thumbnails/{1}'.format(instance.owner.slug, filename)

def icon_upload_to(instance, filename):
    return 'videos/{0}/icons/{1}'.format(instance.owner.slug, filename)
