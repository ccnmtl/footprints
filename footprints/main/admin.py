from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.gis.db.models.fields import PointField
from django.contrib.gis.geos.point import Point
from django.db.models.fields import TextField
from django.forms.widgets import MultiWidget, TextInput
from django.utils.encoding import smart_str
from reversion.admin import VersionAdmin

from footprints.main.models import Footprint, DigitalFormat, Role, \
    ExtendedDate, Actor, Language, DigitalObject, \
    StandardizedIdentification, Person, Place, Collection, WrittenWork, \
    Imprint, BookCopy, StandardizedIdentificationType, CanonicalPlace

from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
actions.add_to_site(site)

admin.site.register(Role)
admin.site.register(DigitalFormat)
admin.site.register(DigitalObject)
admin.site.register(StandardizedIdentificationType)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'marc_code')


admin.site.register(Language, LanguageAdmin)


class StandardizedIdentificationAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'identifier_type')
    list_filter = ('identifier_type',)
    search_fields = ('id', 'name',)


admin.site.register(
    StandardizedIdentification, StandardizedIdentificationAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'death_date', 'gender',
                    'standardized_identifier', 'notes')
    list_filter = ('gender',)
    search_fields = ('name',)


admin.site.register(Person, PersonAdmin)


def imprint_publication_date(obj):
    if obj.imprint:
        return '<a href="/admin/main/imprint/{}"/>Imprint</a>'.format(
            obj.imprint.id)


imprint_publication_date.allow_tags = True


def footprint_associated_date(obj):
    return '<a href="/admin/main/footprint/{}"/>Footprint</a>'.format(
        obj.footprint.id)


footprint_associated_date.allow_tags = True


class ExtendedDateAdmin(admin.ModelAdmin):
    list_display = (
        'edtf_format', '__str__',
        imprint_publication_date, footprint_associated_date)
    search_fields = ('edtf_format',)


admin.site.register(ExtendedDate, ExtendedDateAdmin)


def person_name(obj):
    return obj.person.name


class ActorAdmin(admin.ModelAdmin):

    list_display = (person_name, 'alias', 'role')
    list_filter = ('role__name',)
    person_name.admin_order_field = 'person__name'
    search_fields = ('id', 'alias', 'person__name')


admin.site.register(Actor, ActorAdmin)
admin.site.register(Collection)


class WrittenWorkAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    raw_id_fields = ('actor', 'standardized_identifier')


admin.site.register(WrittenWork, WrittenWorkAdmin)


def imprint_display(obj):
    return smart_str(obj.imprint)


class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('id', imprint_display, 'call_number')
    fields = ('id', 'imprint', 'digital_object', 'notes', 'call_number')
    readonly_fields = ('id',)
    search_fields = ('imprint__title', 'call_number')


admin.site.register(BookCopy, BookCopyAdmin)


def work_title(obj):
    return obj.work.title if obj.work else ''


work_title.short_description = 'Written Work Title'


def language(obj):
    return ', '.join(obj.language.values_list('name', flat=True))


def bhb_number(obj):
    return obj.get_bhb_number()


class ImprintAdmin(admin.ModelAdmin):
    list_display = (work_title, 'title', 'publication_date',
                    language, bhb_number)
    raw_id_fields = ('actor',)
    search_fields = ('title', 'standardized_identifier__identifier')


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
    list_select_related = (
        'book_copy__imprint__publication_date', 'place', 'associated_date')
    list_display = ('id', 'title', 'associated_date', 'place', owner,
                    imprint_title, imprint_date, language, creator,
                    'created_at')
    readonly_fields = ('actor', 'book_copy', 'created_at', 'modified_at',
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
    list_display = ('__str__', 'user', 'action_time')
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


class PlaceInline(admin.TabularInline):
    model = Place
    fields = ['id', 'alternate_name']
    formfield_overrides = {
        TextField: {'widget': TextInput},
    }


class CanonicalPlaceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
        TextField: {'widget': TextInput},
    }
    list_display = (
        'canonical_name', 'geoname_id', 'latitude', 'longitude')
    search_fields = ('canonical_name',)

    inlines = [
        PlaceInline,
    ]


admin.site.register(CanonicalPlace, CanonicalPlaceAdmin)


def canonical_place_id(obj):
    if obj.canonical_place:
        return obj.canonical_place.id


canonical_place_id.short_description = 'Canonical Place Id'


def canonical_name(obj):
    if obj.canonical_place:
        return obj.canonical_place.canonical_name


canonical_name.short_description = 'Canonical Name'


def canonical_latitude(obj):
    if obj.canonical_place:
        return obj.canonical_place.latitude()


canonical_latitude.short_description = 'Canonical Latitude'


def canonical_longitude(obj):
    if obj.canonical_place:
        return obj.canonical_place.longitude()


canonical_longitude.short_description = 'Canonical Longitude'


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'alternate_name', 'canonical_place_id', canonical_name,
        canonical_latitude, canonical_longitude)
    search_fields = ('alternate_name', 'canonical_place__canonical_name')


admin.site.register(Place, PlaceAdmin)
