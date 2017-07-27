from django.contrib.gis.geos.point import Point
from rest_framework.renderers import BrowsableAPIRenderer
from django.utils.encoding import smart_text
from footprints.mixins import BatchAccessMixin, ModerationAccessMixin,\
    AddChangeAccessMixin


def permissions(request):
    return {
        'can_import':
            request.user.has_perms(BatchAccessMixin.permission_required),
        'can_moderate':
            request.user.has_perms(ModerationAccessMixin.permission_required),
        'can_create':
            request.user.has_perms(AddChangeAccessMixin.permission_required)
    }


def interpolate_role_actors(roles, actors):
    ''' Takes in a list of roles and returns a list of actors
    and the role that they have

    The list will take the form of: <Role Name> Actor, <Role Name> Viaf Number
    Within each field there could be multiple actors, and so the subsequent
    field will contain multiple VIAF numbers. These multiple values will be
    separated by a semicolon.'''
    array = []
    for r in roles:
        actor_string = ''
        viaf_string = ''
        # for each actor
        for a in actors:
            # if the actor matches that role
            if r.pk == a.role.id:
                # If the actor string is empty, as it would be on the first
                # iteration, add the actor, else append a semicolon and the
                # actor to the end of the actor string
                if not actor_string:
                    actor_string = smart_text(a).encode('utf-8')
                else:
                    actor_string = '; '.join([actor_string, smart_text(a)
                                              .encode('utf-8')])

                # If the VIAF String is empty, as it would be on the first
                # iteration, add the VIAF number. Else append a semicolon
                # and the VIAF number at the end of the string
                if not viaf_string:
                    viaf_string = a.person.get_viaf_number()
                else:
                    viaf_string = '; '.join([viaf_string,
                                             a.person.get_viaf_number()])

        array.append(actor_string)
        array.append(viaf_string)

    return array


class BrowsableAPIRendererNoForms(BrowsableAPIRenderer):
    '''https://bradmontgomery.net/blog/'''
    '''disabling-forms-django-rest-frameworks-browsable-api/'''

    def get_context(self, *args, **kwargs):
        ctx = super(BrowsableAPIRendererNoForms, self).get_context(
            *args, **kwargs)
        ctx['display_edit_forms'] = False
        return ctx

    def show_form_for_method(self, view, method, request, obj):
        """We never want to do this! So just return False."""
        return False

    def get_rendered_html_form(self, data, view, method, request):
        """Why render _any_ forms at all. This method should return
        rendered HTML, so let's simply return an empty string.
        """
        return ""


def string_to_point(str):
    a = str.split(',')
    return Point(float(a[1].strip()), float(a[0].strip()))
