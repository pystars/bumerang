from django.conf.urls import patterns, url

from .views import FeedbackCreateView


urlpatterns = patterns(
    '',
    url(r'^$', FeedbackCreateView.as_view(), name='feedback'),
)
