from django import template

register = template.Library()


@register.simple_tag
def field_value(batch_row, field):
    return getattr(batch_row, field.name)


@register.simple_tag()
def validate_field_value(row, field, value):
    # required field, null or empty?
    if not value and (not field.null or not field.blank):
        return 'missing has-error'

    # per field validators
    valid = True
    try:
        method_name = 'validate_{}'.format(field.name)
        method = getattr(row, method_name)
        valid = method()
    except AttributeError:
        valid = True  # some fields don't need additional validation

    if valid and not value:
        return 'empty'
    elif valid:
        return 'valid'
    else:
        return 'invalid has-error'
