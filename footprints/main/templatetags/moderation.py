from django import template
from django.db.models.query_utils import Q
from django.db.models import Exists, OuterRef
from django.contrib.auth.models import Group

register = template.Library()


def flag_percent_complete(fp):
    return fp.percent_complete < 50


def flag_empty_narrative(fp):
    return not fp.narrative


def flag_empty_call_number(fp):
    return (fp.medium == 'Bookseller/auction catalog (1850-present)' and
            not fp.call_number)


def flag_empty_bhb_number(fp):
    return not fp.book_copy.imprint.has_bhb_number()


def flag_creator(fp):
    return hasattr(fp, 'new_contributor') and fp.new_contributor


@register.simple_tag
def has_moderation_flags(fp):
    return len(moderation_flags(fp)) > 0


@register.simple_tag
def moderation_flags(fp):
    errors = []
    if flag_empty_call_number(fp):
        errors.append(('err-call-number', 'Catalog\'s call number is empty'))

    if flag_empty_bhb_number(fp):
        errors.append(('err-bhb-number', 'Imprint has no BHB number'))

    if flag_empty_narrative(fp):
        errors.append(('err-narrative', 'Narrative is empty'))

    if flag_percent_complete(fp):
        errors.append(('err-percent-complete',
                       'Percent complete is less than 50%'))

    if flag_creator(fp):
        errors.append(('err-creator',
                       'Created by a new contributor'))

    return errors


def moderation_footprints():
    from footprints.main.models import Footprint, SLUG_BHB

    qs = Footprint.objects.exclude(verified=True).filter(
        Q(percent_complete__lt=50) |
        Q(narrative__isnull=True) |
        Q(created_by__groups__name='Creator') |
        Q(medium='Bookseller/auction catalog (1850-present)',
          call_number__isnull=True) |
        ~Q(book_copy__imprint__standardized_identifier__identifier_type__slug=SLUG_BHB))  # noqa:251

    group = Group.objects.get(name='Creator')
    creators = group.user_set.filter(id=OuterRef('created_by__id'))

    return qs.select_related(
        'created_by', 'last_modified_by',
        'book_copy__imprint').prefetch_related(
        'book_copy__imprint__standardized_identifier__identifier_type').annotate( # noqa:251
            new_contributor=Exists(creators)
    )
