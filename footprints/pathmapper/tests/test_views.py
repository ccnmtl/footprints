from json import loads

from django.test.testcases import TestCase
from django.urls.base import reverse


class BookCopySearchViewTest(TestCase):

    def test_post(self):
        url = reverse('bookcopy-search-view')
        response = self.client.post(url, {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(the_json['total'], 0)
