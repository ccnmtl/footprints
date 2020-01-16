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


class PathmapperTableViewTest(TestCase):

    def test_post(self):
        url = reverse('pathmapper-table-view')
        response = self.client.post(url, {'layers': '{}'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(the_json['count'], 0)
        self.assertEqual(the_json['next'], None)
        self.assertEqual(the_json['previous'], None)
        self.assertEqual(the_json['results'], [])
