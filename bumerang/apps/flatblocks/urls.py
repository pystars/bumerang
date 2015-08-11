try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from .views import edit

urlpatterns = patterns('',
                       url('^edit/(?P<pk>\d+)/$', staff_member_required(edit),
                           name='flatblocks-edit')
                       )
