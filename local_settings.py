# -*- coding: utf-8 -*-
import base64

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = base64.decodestring('YWxleGlsb3Jlbno=')
EMAIL_HOST_PASSWORD = base64.decodestring('YWxza2RqZmhn')
EMAIL_USE_TLS = True
