# -*- coding: utf-8 -*-
from bumerang.apps.utils.signals import file_uploaded
from .signals import transcode_onchange
from .utils import convert_original_video, update_encode_state

file_uploaded.connect(convert_original_video, dispatch_uid='file_uploaded')
transcode_onchange(update_encode_state)
