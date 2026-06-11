from django.contrib import admin
from .models import AlternateMedicine

@admin.register(AlternateMedicine)
class AlternateMedicineAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'alternate_medicine', 'salt_match_percentage', 'is_active', 'created_at')
    list_filter = ('is_active', 'salt_match_percentage', 'created_at')
    search_fields = ('medicine__medicine_name', 'alternate_medicine__medicine_name')
    readonly_fields = ('created_at', 'updated_at')
