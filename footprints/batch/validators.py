from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from edtf.edtf import EDTF


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

    return unicode(EDTF.from_natural_text(value)) != ''


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
