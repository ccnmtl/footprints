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


def stringify_role_actors(roles, actors):
    ''' What does this function do?'''
    string = ''
    for r in roles:
        actor_string = ''
        viaf_string = ''
        for a in actors:
            if r.pk == a.role.id:
                actor_string = smart_text(a) if not actor_string else\
                    '; '.join([actor_string, smart_text(a)])
                viaf_string = a.person.get_viaf_number() if not viaf_string\
                    else '; '.join([viaf_string, a.person.get_viaf_number()])
        if (string == ''):
            string = actor_string
        else:
            string = ','.join([string, actor_string])
        string = ','.join([string, viaf_string])

    import pdb
    pdb.set_trace()
    return string


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
