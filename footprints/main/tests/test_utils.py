from django.test.testcases import TestCase

from footprints.main.utils import interpolate_role_actors
from footprints.main.models import Actor, Role


class CustomUtilsTest(TestCase):

    def test_interpolate_role_actors(self):
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
        self.assertTrue([] == interpolate_role_actors([], []))

        # roles but no actors should return 2 times the number roles as cols
        array = interpolate_role_actors(roles, [])
        self.assertTrue(len(array) == 6)

        # roles and actors should return the string you expect
        array = interpolate_role_actors(roles, actors)
        self.assertTrue(array[0].count('Nick (Author)') == 1)
        self.assertTrue(array[2].count('Nick (Printer)') == 1)
        self.assertTrue(array[4].count('Nick (Censor)') == 1)

        # roles and multiple actors should put all the actors of a given role
        # into the same col
        actor4, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role1, '11/09/84', '11/09/17')
        actors.append(actor4)
        array = interpolate_role_actors(roles, actors)
        self.assertTrue(array[0].count('Nick (Author)') == 2)
        self.assertTrue(array[2].count('Nick (Printer)') == 1)
        self.assertTrue(array[4].count('Nick (Censor)') == 1)
