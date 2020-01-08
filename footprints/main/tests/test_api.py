from json import loads

from django.test.testcases import TestCase

from footprints.main.tests.factories import UserFactory, WrittenWorkFactory, \
    ImprintFactory, FootprintFactory, PersonFactory


class ApiViewTests(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_anonymous(self):
        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

    def test_title_listview(self):
        self.client.login(username=self.user.username, password="test")

        WrittenWorkFactory(title='Alpha')
        ImprintFactory(title='Beta')
        FootprintFactory(title='Gamma')

        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json), 0)

        response = self.client.get('/api/title/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json), 1)
        self.assertEqual(the_json[0], 'Alpha')

    def test_name_listview(self):
        self.client.login(username=self.user.username, password="test")

        PersonFactory(name='Alpha')

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.get('/api/name/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Alpha')
