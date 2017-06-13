from django.contrib import messages
from django.views.generic import CreateView

from .forms import AnonymousFeedbackForm, FeedbackForm


class FeedbackCreateView(CreateView):
    template_name = 'feedback/feedback_form.html'

    def get_form_class(self):
        if self.request.user.is_authenticated():
            return FeedbackForm
        return AnonymousFeedbackForm

    def form_valid(self, form):
        feedback = form.save(commit=False)
        if self.request.user.is_authenticated():
            feedback.user = self.request.user
        feedback.save()
        messages.success(self.request, "Мы получили ваше сообщение.")
        return super(FeedbackCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.request.POST.get(
            'next', self.request.META.get('HTTP_REFERER', '/'))
