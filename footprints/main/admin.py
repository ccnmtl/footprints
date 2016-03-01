from django.contrib import admin
import reversion

from footprints.main.models import Footprint, DigitalFormat, Role, \
    ExtendedDate, Actor, Language, DigitalObject, \
    StandardizedIdentification, Person, Place, Collection, WrittenWork, \
    Imprint, BookCopy, StandardizedIdentificationType


admin.site.register(Role)
admin.site.register(Language)
admin.site.register(DigitalFormat)
admin.site.register(DigitalObject)
admin.site.register(StandardizedIdentification)
admin.site.register(StandardizedIdentificationType)
admin.site.register(Person)


class ExtendedDateAdmin(admin.ModelAdmin):
    list_display = ('edtf_format', '__unicode__')

admin.site.register(ExtendedDate, ExtendedDateAdmin)


def person_name(obj):
    return obj.person.name


class ActorAdmin(admin.ModelAdmin):
    list_display = (person_name, 'alias', 'role')

admin.site.register(Actor, ActorAdmin)

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
    return obj.work.title if obj.work else ''

work_title.short_description = 'Written Work Title'


def language(obj):
    return ', '.join(obj.language.values_list('name', flat=True))


class ImprintAdmin(admin.ModelAdmin):
    list_display = (work_title, 'title', 'publication_date', language)

admin.site.register(Imprint, ImprintAdmin)


def imprint_title(obj):
    if obj.book_copy and obj.book_copy.imprint:
        return obj.book_copy.imprint.title
    else:
        return ''

imprint_title.short_description = 'Imprint Title'


def imprint_date(obj):
    if obj.book_copy and obj.book_copy.imprint:
        return obj.book_copy.imprint.publication_date
    else:
        return ''

imprint_date.short_description = 'Imprint Publication Date'


def owner(obj):
    role = Role.objects.get_owner_role()
    owners = obj.actor.filter(role=role)
    return ", ".join(owners.values_list('person__name', flat=True))

owner.short_description = 'Owner'


class FootprintAdmin(reversion.VersionAdmin):
    list_display = ('title', 'associated_date', 'place', owner,
                    imprint_title, imprint_date, language)
    readonly_fields = ('created_at', 'modified_at',
                       'created_by', 'last_modified_by')
    search_fields = ('title',)
    fieldsets = (
        (None, {
            'fields': ('book_copy', 'medium', 'medium_description',
                       'provenance', 'title', 'language', 'place',
                       'associated_date', 'call_number', 'collection',
                       'digital_object', 'actor', 'notes', 'narrative')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('created_at', 'modified_at',
                       'created_by', 'last_modified_by')
        }),
    )

admin.site.register(Footprint, FootprintAdmin)
