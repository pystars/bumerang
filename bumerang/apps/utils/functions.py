# -*- coding: utf-8 -*-
import os
import random
import string
from tempfile import TemporaryFile

from PIL import Image
from django.conf import settings
from django.core.files.storage import get_storage_class, FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile


def random_string(length, letters=string.ascii_letters + string.digits):
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


def image_crop_rectangle_center(img):
    """
    Crops rectangle region from center of given image
    """
    width = img.size[0]
    height = img.size[1]

    if height > width:
        diff = height - width
        half_diff = int(round(diff/2))

        img = img.crop((
            0,
            half_diff,
            width,
            width + half_diff
        ))

    if height < width:
        diff = width - height
        half_diff = int(round(diff/2))

        img = img.crop((
            half_diff,
            0,
            height + half_diff,
            height
        ))

    if height == width:
        pass

    return img


def get_path(pattern, pk_dir_name=False):
    """
    callable function for upload_to param of models fields

    if pk_dir_name, then pk of object used as dir name
    """
    def inner(instance, filename):
        ext = os.path.splitext(filename)[1]
        if pk_dir_name:
            dir_name = instance.id
        else:
            dir_name = random_string(12)
        rel_path = pattern.format(dir_name, ext)
        if issubclass(get_storage_class(), FileSystemStorage):
            path = os.path.split(os.path.join(settings.MEDIA_ROOT, rel_path))[0]
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError:
                    pass
        return rel_path
    return inner
