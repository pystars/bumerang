# -*- coding: utf-8 -*-
import os
import random
import string
from tempfile import TemporaryFile
from exceptions import TypeError, OSError

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

def random_string(length, letters=string.ascii_letters+string.digits):
    return u''.join(random.choice(letters) for i in xrange(length))

def thumb_img(img, width=None, height=None, name='thumb.jpg'):
    io = TemporaryFile()
    thumb = img.copy()
    thumb.thumbnail(image_width_height(img, width, height), Image.ANTIALIAS)
    thumb.save(io, format='JPEG', quality=100)
    del thumb
    size = io.tell()
    io.seek(0)
    return InMemoryUploadedFile(io, None, name, 'image/jpeg', size, None)

def thumb_crop_img(img, width=None, height=None, name='thumb.jpg'):
    """
    Resizes image and crop him if it due proportions
    """
    io = TemporaryFile()
    thumb = img.copy()
    thumb.thumbnail(image_width_height(img, width=width), Image.ANTIALIAS)
    if thumb.size[1] >= height:
        thumb = thumb.crop((0, 0, width, height))
    else:
        thumb = thumb.resize((width, height), Image.ANTIALIAS)
    thumb.save(io, format='JPEG', quality=100)
    del thumb
    size = io.tell()
    io.seek(0)
    return InMemoryUploadedFile(io, None, name, 'image/jpeg', size, None)

def image_width_height(img, width=None, height=None):
    try:
        width, height = int(width), int(height)
    except TypeError:
        pass
    if width and height:
        return width, height
    img_width, img_height = img.size
    if not (width or height):
        return img_width, img_height
    if not width:
        width = int(img_width * float(height) / img_height)
    elif not height:
        height = int(img_height * float(width) / img_width)
    return width, height

def get_path(pattern):
    def inner(instance, filename):
        ext = os.path.splitext(filename)[1]
        rel_path = pattern.format(random_string(12), ext)
        path = os.path.split(os.path.join(settings.MEDIA_ROOT, rel_path))[0]
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                pass
        return rel_path
    return inner