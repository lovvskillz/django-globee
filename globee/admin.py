from django.contrib import admin

from globee.models import GlobeeIPN


class GlobeeIPNAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'payment_status', 'total', 'currency', 'custom_payment_id', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('payment_id', 'custom_payment_id')


admin.site.register(GlobeeIPN, GlobeeIPNAdmin)
