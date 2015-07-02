# -*- coding: utf-8 -*-
import json

from django.core.signing import JSONSerializer
from django.core.serializers.json import DjangoJSONEncoder


class SessionJSONSerializer(JSONSerializer):
    def dumps(self, obj):
        return json.dumps(
            obj, cls=DjangoJSONEncoder, separators=(',', ':')).encode('latin-1')
