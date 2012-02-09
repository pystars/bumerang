# -*- coding: utf-8 -*-


nullable = dict(null=True, blank=True)
choices = lambda *x: zip(x,x)

class TitleUnicode(object):
    title = ''
    def __unicode__(self):
        return u'{0}'.format(self.title)
