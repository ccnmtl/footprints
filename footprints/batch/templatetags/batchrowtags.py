from django import template
from footprints.batch import validators

register = template.Library()


@register.assignment_tag
def field_value(batch_row, field):
    return getattr(batch_row, field.name)


@register.simple_tag()
def validate_field_value(field, value):
    # required field, null or empty?
    if value is None:
        return 'empty' if field.null else 'missing has-error'

    if len(value) < 1:
        return 'empty' if field.blank else 'missing has-error'

    # per field validators
    valid = True
    try:
        method_name = 'validate_{}'.format(field.name)
        method = getattr(validators, method_name)
        valid = method(value)
    except AttributeError:
        valid = True

    return 'valid' if valid else 'invalid has-error'
