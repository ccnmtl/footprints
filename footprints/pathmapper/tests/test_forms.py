from django.test.testcases import TestCase

from footprints.pathmapper.forms import BookCopySearchForm


class BookCopySearchFormTest(TestCase):

    def test_empty_search(self):
        form = BookCopySearchForm()
        form.cleaned_data = {}
        form.data = {
            'work': None,
            'imprint': None,
            'imprintLocation': None,
            'footprintLocation': None,
            'footprintStart': None,
            'footprintEnd': None,
            'pubStart': None,
            'pubEnd': None
        }
        sqs = form.search()
        self.assertEqual(sqs.count(), 0)

    def test_form_clean_errors_future_date(self):
        form = BookCopySearchForm()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintStart': 2080,
            'footprintEnd': 2080,
            'pubStart': None,
            'pubEnd': None
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'], ['No future year'])
        self.assertTrue(form._errors['footprintEnd'], ['No future year'])

    def test_form_clean_errors_past_date(self):
        form = BookCopySearchForm()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintStart': 999,
            'footprintEnd': 999,
            'pubStart': 999,
            'pubEnd': 999
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['footprintEnd'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['pubStart'],
                        ['Year must be greater than 1000'])
        self.assertTrue(form._errors['pubEnd'],
                        ['Year must be greater than 1000'])

    def test_form_clean_range(self):
        form = BookCopySearchForm()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': True,
            'footprintStart': 2016,
            'footprintEnd': 1740,
            'pubStart': None,
            'pubEnd': None
        }

        form.clean()
        self.assertTrue(form._errors['footprintStart'],
                        ['Start year must be less than end year'])

    def test_form_clean_single_year_valid(self):
        form = BookCopySearchForm()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': False,
            'footprintStart': 1740,
            'footprintEnd': None,
            'pubStart': 1740,
            'pubEnd': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_range_valid(self):
        form = BookCopySearchForm()
        form._errors = {}
        form.cleaned_data = {}
        form.data = {
            'q': '',
            'footprintRange': '1',
            'footprintStart': None,
            'footprintEnd': 1740,
            'pubStart': None,
            'pubEnd': 1740
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)
