# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from bumerang.apps.utils.functions import image_crop_rectangle_center

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from PIL import Image
from celery.task import Task

from bumerang.apps.accounts.models import Teammate, Teacher


def convert_photos(model_instance):
    photo = model_instance.photo

    # setting read pointer to beginning of the file
    photo.file.seek(0)
    # loading image into memory
    original_image = Image.open(photo)
    memory_file = StringIO()
    # setting up correct mode
    if original_image.mode not in ('L', 'RGB'):
        original_image = original_image.convert('RGB')

    # if width is greater, then resize image
    MAX_WIDTH = 800

    if original_image.size[0] > MAX_WIDTH:
        aspect = original_image.size[0] / MAX_WIDTH
        new_height = int(round(original_image.size[1] / aspect))
        original_image = original_image.resize(
            (MAX_WIDTH, new_height), Image.ANTIALIAS)

    # storing image into memory file
    original_image.save(memory_file, 'jpeg')
    memory_file.seek(0)

    # deleting old image file
    model_instance.photo.delete()
    # and saving new processed original image
    model_instance.photo.save(
        '{oid}-{id}-full.jpg'.format(
            oid=model_instance.owner.id,
            id=model_instance.id
        ),
        ContentFile(memory_file.read())
    )

    # loading original image, already normalized
    minified_image = Image.open(model_instance.photo)

    minified_image = image_crop_rectangle_center(minified_image)

    minified_image.thumbnail((125, 125), Image.ANTIALIAS)

    # reinitialize memory file
    memory_file = StringIO()
    minified_image.save(memory_file, 'jpeg')
    memory_file.seek(0)

    model_instance.photo_min.save(
        '{oid}-{id}-min.jpg'.format(
            oid=model_instance.owner.id,
            id=model_instance.id
        ),
        ContentFile(memory_file.read())
    )


class ConvertTeamAndTeachers(Task):

    teammates = Teammate.objects.all()

    for teammate in teammates:
        convert_photos(teammate)

    teachers = Teacher.objects.all()

    for teacher in teachers:
        convert_photos(teacher)
