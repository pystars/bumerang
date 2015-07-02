# -*- coding: utf-8 -*-
import json

from django.core.serializers.json import DjangoJSONEncoder


class SessionJSONSerializer(object):
    def dumps(self, obj):
        return json.dumps(
            obj, cls=DjangoJSONEncoder, separators=(',', ':')).encode('latin-1')

    def loads(self, data):
        return json.loads(data.decode('latin-1'), cls=DjangoJSONEncoder)
