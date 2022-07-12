from django.db.models.query_utils import Q
from django.test.testcases import TestCase

from footprints.main.forms import FootprintSearchForm, ContactUsForm, \
    ExtendedDateForm
from footprints.main.models import ExtendedDate


class FootprintSearchFormTest(TestCase):

    def test_empty_search(self):
        form = FootprintSearchForm()
        form.cleaned_data = {
            'q': '',
            'search_level': True,
            'footprint_start_year': None,
            'footprint_end_year': None,
            'pub_start_year': None,
            'pub_end_year': None,
            'actor': [],
            'footprint_location': [],
            'imprint_location': []
        }
        sqs = form.search()
        self.assertEqual(sqs.count(), 0)

    def test_form_clean_empty(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'search_level': True,
            'footprint_start_year': None,
            'footprint_end_year': None,
            'pub_start_year': None,
            'pub_end_year': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 1)
        self.assertTrue('q' in form._errors)

    def test_form_clean_xss(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': 'oppenheim',
            'direction': 'asc',
            'footprint_start_year': "<script>alert('foo');</script>",
            'sort_by': 'ftitle'
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_q(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': 'oppenheim',
            'footprint_start_year': None,
            'footprint_end_year': None,
            'pub_start_year': None,
            'pub_end_year': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_errors_future_date(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_start_year': 2080,
            'footprint_end_year': 2080,
            'pub_start_year': None,
            'pub_end_year': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 2)
        self.assertTrue('footprint_start_year' in form._errors)
        self.assertTrue('footprint_end_year' in form._errors)

    def test_form_clean_errors_past_date(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_start_year': 999,
            'footprint_end_year': 999,
            'pub_start_year': 999,
            'pub_end_year': 999
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 4)
        self.assertTrue('footprint_start_year' in form._errors)
        self.assertTrue('footprint_end_year' in form._errors)
        self.assertTrue('pub_start_year' in form._errors)
        self.assertTrue('pub_end_year' in form._errors)

    def test_form_clean_range(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '1',
            'footprint_start_year': 2016,
            'footprint_end_year': 1740,
            'pub_start_year': None,
            'pub_end_year': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 1)
        self.assertTrue('footprint_start_year' in form._errors)

    def test_form_clean_single_year_valid(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '0',
            'footprint_start_year': 1740,
            'footprint_end_year': None,
            'pub_start_year': 1740,
            'pub_end_year': None
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_range_valid(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '1',
            'footprint_start_year': None,
            'footprint_end_year': 1740,
            'pub_start_year': None,
            'pub_end_year': 1740
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_handle_image(self):
        form = FootprintSearchForm()
        form.cleaned_data = {
            'q': '',
            'search_level': True,
            'footprint_start_year': None,
            'footprint_end_year': None,
            'pub_start_year': None,
            'pub_end_year': None,
            'actor': [],
            'footprint_location': [],
            'imprint_location': [],
            'gallery_view': True
        }
        a = ['prior']
        form.handle_image(a)
        self.assertIn('prior', a)
        self.assertIn(Q(has_image=True), a)

    def test_handle_creator(self):
        form = FootprintSearchForm()

        q = 'a b'
        a = []
        self.assertEqual('a b', form.handle_creator(q, a))
        self.assertEqual(a, [])

        q = 'a b creator:username'
        a = []
        self.assertEqual('a b ', form.handle_creator(q, a))
        self.assertEqual(a, [Q(creator__contains='username')])

        q = 'creator:username a b'
        a = []
        self.assertEqual(' a b', form.handle_creator(q, a))
        self.assertEqual(a, [Q(creator__contains='username')])

        q = 'a creator:username b'
        a = ['prior']
        self.assertEqual('a  b', form.handle_creator(q, a))
        self.assertEqual(a, ['prior', Q(creator__contains='username')])


class ContactUsFormTest(TestCase):

    def test_form_clean(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': '',
            'subject': 'other'
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 0)

    def test_form_clean_no_subject(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': '',
            'description': 'Lorem Ipsum',
            'email': 'jdoe@foo.com',
            'name': 'Jane Doe'
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 1)
        self.assertTrue('subject' in form._errors)

    def test_form_clean_no_decoy(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'subject': '',
            'description': 'Lorem Ipsum',
            'email': 'jdoe@foo.com',
            'name': 'Jane Doe'
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 1)
        self.assertTrue('decoy' in form._errors)

    def test_form_clean_errors(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': 'foo',
            'subject': '-----'
        }

        form.clean()
        self.assertEqual(len(form._errors.keys()), 2)
        self.assertTrue('decoy' in form._errors)
        self.assertTrue('subject' in form._errors)


class ExtendedDateFormTest(TestCase):

    def test_get_attr(self):
        form = ExtendedDateForm()
        form.cleaned_data = {'attr': 'foo'}
        self.assertEqual(form.get_attr(), 'foo')

    def test_clean_empty_fields(self):
        data = {
            'is_range': True,
            'millenium1': None, 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '1', 'day1': '1',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': '0', 'decade2': None, 'year2': '1',
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'Please fill out all required fields<br />')

        data['millenium1'] = 2
        data['millenium2'] = 2
        ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'Please fill out all required fields<br />')

    def test_clean_valid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(ExtendedDate.objects.count(), 0)

    def test_clean_valid_date_range(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '0', 'decade2': '1', 'year2': '2',
            'month2': '2', 'day2': '29',
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_error_messages(), '')
        self.assertEqual(ExtendedDate.objects.count(), 0)

        dt = form.save()
        self.assertEqual(ExtendedDate.objects.count(), 1)
        self.assertEqual(dt.edtf_format, '2010-02-28?~/2012-02-29')

    def test_clean_invalid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '2', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'Please specify a valid date<br />')

        data['day1'] = 28
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'The date must be today or earlier<br />')

    def test_clean_invalid_date_ranges(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '2', 'decade1': '1', 'year1': '0',
            'month1': '6', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '2', 'decade2': '0', 'year2': '9',
            'month2': '9', 'day2': '31',
            'approximate2': False, 'uncertain2': False,
        }

        # invalid start date
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'Please specify a valid start date<br />')
        self.assertEqual(ExtendedDate.objects.count(), 0)

        # invalid end date
        data['day1'] = '30'
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.get_error_messages(),
            u'Please specify a valid end date<br />')
        self.assertEqual(ExtendedDate.objects.count(), 0)

        # start year in the future
        data['day2'] = 30
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'All dates must be today or earlier<br />')
        self.assertEqual(ExtendedDate.objects.count(), 0)

        # end year in the future
        data['century1'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_error_messages(),
                         u'All dates must be today or earlier<br />')
        self.assertEqual(ExtendedDate.objects.count(), 0)

        # start > end
        data['century2'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.get_error_messages(),
            u'The start date must be earlier than the end date.<br />')
        self.assertEqual(ExtendedDate.objects.count(), 0)

    def test_clean_incomplete_data(self):
        data = {
            'approximate1': True, 'approximate2': False, 'attr': u'',
            'century1': None, 'century2': None, 'day1': None, 'day2': None,
            'decade1': None, 'decade2': None, 'is_range': False,
            'millenium1': 1, 'millenium2': None,
            'month1': None, 'month2': None,
            'uncertain1': True, 'uncertain2': False,
            'year1': None, 'year2': None
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())

        self.assertEqual(form.get_error_messages(),
                         u'Please specify a valid date<br />')
