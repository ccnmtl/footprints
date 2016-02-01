from django import template

from footprints.batch.models import BatchRow


register = template.Library()


@register.simple_tag(takes_context=True)
def field_verbose_name(context, field_name):
    return BatchRow._meta.get_field_by_name(field_name)[0].verbose_name.title()


@register.simple_tag(takes_context=True)
def field_value(context, batch_row, field_name):
    return getattr(batch_row, field_name)


@register.simple_tag(takes_context=True)
def field_validate(context, batch_row, field_name):
    # required field, empty?
    value = getattr(batch_row, field_name)
    field = BatchRow._meta.get_field_by_name(field_name)[0]

    if value is None:
        return 'empty' if field.null else 'missing'

    if len(value) < 1:
        return 'empty' if field.blank else 'missing'

    valid = True
    try:
        method_name = 'validate_{}'.format(field_name)
        method = getattr(batch_row, method_name)
        valid = method()
    except AttributeError:
        valid = True

    return 'valid' if valid else 'invalid'
