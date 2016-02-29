import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from edtf.edtf import EDTF

from footprints.main.models import Role, MEDIUM_CHOICES


def validate_catalog_url(value):
    try:
        if value:
            URLValidator()(value)
        return True
    except ValidationError:
        return False


def validate_date(value):
    if value is None or len(value) < 1:
        return True

    s = unicode(EDTF.from_natural_text(value))
    return s != '' and 'invalid' not in s


def validate_writtenwork_author_birth_date(value):
    return validate_date(value)


def validate_writtenwork_author_death_date(value):
    return validate_date(value)


def validate_publication_date(value):
    return validate_date(value)


def validate_footprint_actor_birth_date(value):
    return validate_date(value)


def validate_footprint_actor_death_date(value):
    return validate_date(value)


def validate_footprint_date(value):
    return validate_date(value)


def validate_numeric(value):
    if value is None or len(value) < 1:
        return True

    return re.match(r'^[0-9]*$', value) is not None


def validate_bhb_number(value):
    return validate_numeric(value)


def validate_writtenwork_author_viaf(value):
    return validate_numeric(value)


def validate_publisher_viaf(value):
    return validate_numeric(value)


def validate_footprint_actor_viaf(value):
    return validate_numeric(value)


def validate_footprint_actor_role(value):
    if value is None or len(value) < 1:
        return True

    return Role.objects.for_footprint().filter(name=value).first() is not None


def validate_medium(value):
    if value is None or len(value) < 1:
        return True

    return value in MEDIUM_CHOICES


def validate_latlng(value):
    if value is None or len(value) < 1:
        return True
    pattern = r'^[-+]?\d{1,2}([.]\d+)?,\s*[-+]?\d{1,3}([.]\d+)?$'
    return re.match(pattern, value) is not None


def validate_footprint_location(value):
    return validate_latlng(value)


def validate_publication_location(value):
    return validate_latlng(value)
