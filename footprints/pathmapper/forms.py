from django import forms
from footprints.main.models import BookCopy
from haystack.forms import ModelSearchForm


class BookCopySearchForm(ModelSearchForm):

    work = forms.IntegerField(required=False)
    imprint = forms.IntegerField(required=False)

    class Meta:
        model = BookCopy

    def search(self):
        args = []
        kwargs = {
            'django_ct': 'main.bookcopy',
        }

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['imprint_id'] = imprint_id

        return self.searchqueryset.filter(*args, **kwargs)
