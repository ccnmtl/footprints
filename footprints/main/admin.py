from django.contrib import admin

from footprints.main.models import Footprint, DigitalFormat, Role, \
    Name, ExtendedDateFormat, Contributor, Language, DigitalObject, \
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
admin.site.register(Contributor)
admin.site.register(Place)
admin.site.register(Collection)
admin.site.register(WrittenWork)
admin.site.register(Imprint)
admin.site.register(BookCopy)
admin.site.register(Footprint)
