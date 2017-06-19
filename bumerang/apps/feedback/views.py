# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import CreateView

from .forms import FeedbackForm


class FeedbackCreateView(CreateView):
    template_name = 'feedback/feedback_form.html'

    form_class = FeedbackForm

    def form_valid(self, form):
        feedback = form.save(commit=False)
        if self.request.user.is_authenticated():
            feedback.user = self.request.user
        feedback.save()
        messages.success(self.request, u"Мы получили ваше сообщение.")
        return super(FeedbackCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.request.POST.get(
            'next', self.request.META.get('HTTP_REFERER', '/'))
