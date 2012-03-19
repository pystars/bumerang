# -*- coding: utf-8 -*-
import random
import string
from cStringIO import StringIO
from exceptions import TypeError

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

def random_string(length, letters=string.ascii_letters+string.digits):
    return u''.join(random.choice(letters) for i in xrange(length))

def thumb_img(img, width=None, height=None):
    io = StringIO()
    thumb = img.copy()
    thumb.thumbnail(image_width_height(img, width, height), Image.ANTIALIAS)
    thumb.save(io, format='JPEG')
    size = io.tell()
    io.seek(0)
    return InMemoryUploadedFile(io, None, 'thumb.jpg', 'tmp/jpeg', size, None)


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