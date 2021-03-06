import re
from django.utils.encoding import smart_text
from edtf.edtf import EDTF


def validate_date(value):
    if not value:
        return True

    try:
        s = smart_text(EDTF.from_natural_text(value))
        return s != '' and 'invalid' not in s
    except OverflowError:
        return False


def validate_numeric(value):
    if not value:
        return True

    return re.match(r'^[0-9]*$', value) is not None
