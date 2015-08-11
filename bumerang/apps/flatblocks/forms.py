from django.forms import ModelForm

from .models import FlatBlock


class FlatBlockForm(ModelForm):
    class Meta:
        model = FlatBlock
        exclude = ('slug', 'site')
