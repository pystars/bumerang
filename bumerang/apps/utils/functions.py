# -*- coding: utf-8 -*-
import random
import string

def random_string(length, letters=string.ascii_letters+string.digits):
    return u''.join(random.choice(letters) for i in xrange(length))
