from rest_framework.renderers import BrowsableAPIRenderer

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
