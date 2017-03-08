from footprints.mixins import BatchAccessMixin, ModerationAccessMixin,\
    AddChangeAccessMixin


def permissions(request):
    return {
        'can_import':
            request.user.has_perms(BatchAccessMixin.permission_required),
        'can_moderate':
            request.user.has_perms(ModerationAccessMixin.permission_required),
        'can_edit':
            request.user.has_perms(AddChangeAccessMixin.permission_required)
    }
