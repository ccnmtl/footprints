from django import template

register = template.Library()


@register.simple_tag
def book_copy_footprints(fp):
    qs = fp.book_copy.footprint_set.all().exclude(pk=fp.pk)
    lst = list(qs)
    lst.sort(key=lambda obj: obj.sort_date())
    return lst
