# -*- coding: utf-8 -*-levf.
import os

def original_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'photos/{0}/original{1}'.format(instance.slug, ext)

def image_upload_to(instance, filename):
    return 'photos/{0}/image.jpg'.format(instance.slug)

def thumbnail_upload_to(instance, filename):
    return 'photos/{0}/thumbnail.jpg'.format(instance.slug)

def icon_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'photos/{0}/icon.jpg'.format(instance.slug)



