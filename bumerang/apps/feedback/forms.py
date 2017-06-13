from django import forms

from .models import AnonymousFeedback, Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('user', 'time')


class AnonymousFeedbackForm(forms.ModelForm):
    class Meta:
        model = AnonymousFeedback
        exclude = ('user', 'time')
