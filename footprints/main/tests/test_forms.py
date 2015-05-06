from django import forms
from django.test.testcases import TestCase

from footprints.main.forms import FootprintSearchForm


class SearchFormTest(TestCase):

    def test_init(self):
        form = FootprintSearchForm()

        self.assertEquals(type(form.fields['models']),
                          forms.MultipleChoiceField)

        self.assertEquals(form.fields['q'].widget.attrs['class'],
                          'form-control')

        self.assertEquals(form.fields['q'].widget.attrs['placeholder'],
                          'Titles, People, Places')

    def test_empty_search(self):
        form = FootprintSearchForm()
        sqs = form.search()
        self.assertEquals(sqs.count(), 0)
