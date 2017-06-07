from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.gis.db.models.fields import PointField
from django.contrib.gis.geos.point import Point
from django.forms.widgets import MultiWidget, TextInput
from reversion.admin import VersionAdmin

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


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'death_date',
                    'standardized_identifier', 'notes')
    search_fields = ('name',)


admin.site.register(Person, PersonAdmin)


class ExtendedDateAdmin(admin.ModelAdmin):
    list_display = ('edtf_format', '__unicode__')


admin.site.register(ExtendedDate, ExtendedDateAdmin)


def person_name(obj):
    return obj.person.name


class ActorAdmin(admin.ModelAdmin):

    list_display = (person_name, 'alias', 'role')
    person_name.admin_order_field = 'person__name'


admin.site.register(Actor, ActorAdmin)
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
    role, created = Role.objects.get_or_create(name=Role.OWNER)
    owners = obj.actor.filter(role=role)
    return ", ".join(owners.values_list('person__name', flat=True))


owner.short_description = 'Owner'


def creator(obj):
    return obj.created_by.get_full_name()


class FootprintAdmin(VersionAdmin):
    list_display = ('title', 'associated_date', 'place', owner,
                    imprint_title, imprint_date, language, creator)
    readonly_fields = ('created_at', 'modified_at',
                       'created_by', 'last_modified_by')
    search_fields = ('title',
                     'created_by__last_name', 'created_by__first_name')
    fieldsets = (
        (None, {
            'fields': ('book_copy', 'medium', 'medium_description',
                       'provenance', 'title', 'language', 'place',
                       'associated_date', 'call_number', 'collection',
                       'digital_object', 'actor', 'notes', 'narrative',
                       'verified')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('created_at', 'modified_at',
                       'created_by', 'last_modified_by')
        }),
    )


admin.site.register(Footprint, FootprintAdmin)


class LogEntryAdmin(VersionAdmin):
    list_display = ('__unicode__', 'user', 'action_time')
    search_fields = ('user',)


admin.site.register(LogEntry, LogEntryAdmin)


class LatLongWidget(MultiWidget):
    """
    A Widget that splits Point input into latitude/longitude text inputs.
    http://stackoverflow.com/a/33339847
    """

    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (TextInput(attrs=attrs), TextInput(attrs=attrs))
        super(LatLongWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value.coords[1], value.coords[0])
        return (None, None)

    def value_from_datadict(self, data, files, name):
        lat = data[name + '_0']
        lng = data[name + '_1']

        try:
            point = Point(float(lng), float(lat))
        except ValueError:
            return ''

        return point


class PlaceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
    }
    list_display = ('city', 'country', 'latitude', 'longitude')
    search_fields = ('city', 'country',)


admin.site.register(Place, PlaceAdmin)
