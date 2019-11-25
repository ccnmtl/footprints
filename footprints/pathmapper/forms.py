from django import forms
from footprints.main.models import BookCopy
from haystack.forms import ModelSearchForm


class BookCopySearchForm(ModelSearchForm):

    work = forms.IntegerField(required=False)
    imprint = forms.IntegerField(required=False)
    imprint_location = forms.IntegerField(required=False)
    footprint_location = forms.IntegerField(required=False)

    class Meta:
        model = BookCopy

    def clean_imprint_location(self):
        if 'imprintLocation' in self.data:
            return self.data['imprintLocation']
        else:
            return ''

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

        imprint_loc = self.cleaned_data.get('imprint_location')
        if imprint_loc:
            kwargs['imprint_location'] = imprint_loc

        footprint_loc = self.cleaned_data.get('footprint_location')
        if footprint_loc:
            kwargs['footprint_location'] = footprint_loc

        return self.searchqueryset.filter(*args, **kwargs)
