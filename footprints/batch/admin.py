from django.contrib import admin
from footprints.batch.models import BatchJob, BatchRow

admin.site.register(BatchJob)


class BatchRowAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'publication_date', 'footprint_date')


admin.site.register(BatchRow, BatchRowAdmin)
