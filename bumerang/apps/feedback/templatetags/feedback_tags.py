from itertools import chain

from django.conf import settings
from django.template import Library, Node

from ..models import Feedback


register = Library()


@register.tag
def get_feedback(parser, token):
    '''
    {% get_feedback %}
    '''
    return FeedbackNode()


class FeedbackNode(Node):
    def render(self, context):
        feedback = [Feedback.objects.all()]
        # Flatten list of querysets and sort feedback by date.
        feedback = sorted(list(chain.from_iterable(feedback)),
                          key=lambda instance: instance.time, reverse=True)
        context['feedback'] = feedback
        return ''
