from django import template

register = template.Library()


@register.simple_tag
def book_copy_footprints(fp):
    return fp.book_copy.footprint_set.all().exclude(pk=fp.pk)
