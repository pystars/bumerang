# -*- coding: utf-8 -*-
from django.dispatch import Signal

transcode_onchange = Signal(providing_args=["message"])
