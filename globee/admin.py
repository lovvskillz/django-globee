from django.contrib import admin

from globee.models import GlobeeIPN


class GlobeeIPNAdmin(admin.ModelAdmin):
    list_display = ('pk', 'payment_status', 'payment_id', 'total', 'currency', 'custom_payment_id', 'created_at')


admin.site.register(GlobeeIPN, GlobeeIPNAdmin)

