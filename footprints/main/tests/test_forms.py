from django import forms
from django.test.testcases import TestCase

from footprints.main.forms import FootprintSearchForm, ContactUsForm


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


class ContactUsFormTest(TestCase):

    def test_form_clean(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': '',
            'subject': 'other'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_form_clean_errors(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': 'foo',
            'subject': '-----'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('decoy' in form._errors)
        self.assertTrue('subject' in form._errors)
