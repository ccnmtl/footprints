from django.contrib import admin

from footprints.main.models import Footprint, DigitalFormat, Role, \
    Name, ExtendedDateFormat, Actor, Language, DigitalObject, \
    StandardizedIdentification, Person, Place, Collection, WrittenWork, \
    Imprint, BookCopy


admin.site.register(ExtendedDateFormat)
admin.site.register(Role)
admin.site.register(Name)
admin.site.register(Language)
admin.site.register(DigitalFormat)
admin.site.register(DigitalObject)
admin.site.register(StandardizedIdentification)
admin.site.register(Person)
admin.site.register(Actor)
admin.site.register(Place)
admin.site.register(Collection)
admin.site.register(WrittenWork)
admin.site.register(BookCopy)


def work_title(obj):
    if obj.work:
        return obj.work.title
    else:
        return ''

work_title.short_description = 'Written Work Title'


class ImprintAdmin(admin.ModelAdmin):
    list_display = (work_title, 'title', 'date_of_publication')

admin.site.register(Imprint, ImprintAdmin)


def imprint_title(obj):
    if obj.book_copy and obj.book_copy.imprint:
        return obj.book_copy.imprint.title
    else:
        return ''

imprint_title.short_description = 'Imprint Title'


def imprint_date(obj):
    if obj.book_copy and obj.book_copy.imprint:
        return obj.book_copy.imprint.date_of_publication
    else:
        return ''

imprint_date.short_description = 'Imprint Publication Date'


def footprint_date(obj):
    return obj.associated_date

footprint_date.short_description = 'Footprint Date'


def footprint_place(obj):
    return obj.place

footprint_place.short_description = 'Footprint Place'


def owner(obj):
    role = Role.objects.get_owner_role()
    owners = obj.actor.filter(role=role)
    return ", ".join(owners.values_list('person__name__name', flat=True))

owner.short_description = 'Owner'


class FootprintAdmin(admin.ModelAdmin):
    list_display = ('title', footprint_date, footprint_place, owner,
                    imprint_title, imprint_date,)

admin.site.register(Footprint, FootprintAdmin)
