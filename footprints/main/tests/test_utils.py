from django.test.testcases import TestCase

from footprints.main.utils import stringify_role_actors
from footprints.main.models import Actor, Role


class CustomUtilsTest(TestCase):

    def test_stringify_role_actors(self):
        roles = []
        actors = []

        role1, created = Role.objects.get_or_create(name='Author')
        role2, created = Role.objects.get_or_create(name='Printer')
        role3, created = Role.objects.get_or_create(name='Censor')
        roles = [role1, role2, role3]

        actor1, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role1, '11/09/84', '11/09/17')
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role2, '11/09/84', '11/09/17')
        actor3, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role3, '11/09/84', '11/09/17')
        actors = [actor1, actor2, actor3]
        # no roles or actors
        self.assertTrue('' == stringify_role_actors([], []))

        # roles but no actors should return 2 times the number roles as cols
        string = stringify_role_actors(roles, [])
        self.assertTrue(string.count(',') == 5)

        # roles and actors should return the string you expect
        string = stringify_role_actors(roles, actors)
        self.assertTrue(string.count('Nick (Author)') == 1)
        self.assertTrue(string.count('Nick (Printer)') == 1)
        self.assertTrue(string.count('Nick (Censor)') == 1)
        self.assertTrue(string.count('1234') == 3)

        # roles and multiple actors should put all the actors of a given role
        # into the same col
        actor4, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role1, '11/09/84', '11/09/17')
        actors.append(actor4)
        string = stringify_role_actors(roles, actors)
        self.assertTrue(string.count('Nick (Author)') == 2)
        self.assertTrue(string.count('Nick (Printer)') == 1)
        self.assertTrue(string.count('Nick (Censor)') == 1)
        self.assertTrue(string.count('1234') == 4)
