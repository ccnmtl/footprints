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


def imprint_display(obj):
    return obj.imprint.__unicode__()


class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('id', imprint_display)
    fields = ('id', 'imprint', 'digital_object', 'notes')
    readonly_fields = ('id',)

admin.site.register(BookCopy, BookCopyAdmin)


def work_title(obj):
    if obj.work:
        return obj.work.title
    else:
        return ''

work_title.short_description = 'Written Work Title'


def language(obj):
    return ', '.join(obj.language.values_list('name', flat=True))


class ImprintAdmin(admin.ModelAdmin):
    list_display = (work_title, 'title', 'date_of_publication', language)

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


def owner(obj):
    role = Role.objects.get_owner_role()
    owners = obj.actor.filter(role=role)
    return ", ".join(owners.values_list('person__name__name', flat=True))

owner.short_description = 'Owner'


class FootprintAdmin(admin.ModelAdmin):
    list_display = ('title', 'associated_date', 'place', owner,
                    imprint_title, imprint_date,)

admin.site.register(Footprint, FootprintAdmin)
