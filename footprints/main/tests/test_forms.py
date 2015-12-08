from django import forms
from django.test.testcases import TestCase

from footprints.main.forms import FootprintSearchForm, ContactUsForm, \
    ExtendedDateForm


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


class ExtendedDateFormTest(TestCase):

    def test_get_attr(self):
        form = ExtendedDateForm()
        form.cleaned_data = {'attr': 'foo'}
        self.assertEquals(form.get_attr(), 'foo')

    def test_clean(self):
        data = {
            'millenium1': None, 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '1', 'day1': '1',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': '0', 'decade2': None, 'year2': '1',
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        self.assertFalse(ExtendedDateForm(data=data).is_valid())

        data['millenium1'] = 2
        data['millenium2'] = 2
        self.assertFalse(ExtendedDateForm(data=data).is_valid())

        data['year2'] = None
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.get_edtf().edtf_format,
                          '2010-01-01?~/20xx')
