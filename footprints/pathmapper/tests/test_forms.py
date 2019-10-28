from django.test.testcases import TestCase

from footprints.pathmapper.forms import BookCopySearchForm


class BookCopySearchFormTest(TestCase):

    def test_empty_search(self):
        form = BookCopySearchForm()
        form.cleaned_data = {
            'work': None,
            'imprint': None
        }
        sqs = form.search()
        self.assertEquals(sqs.count(), 0)
