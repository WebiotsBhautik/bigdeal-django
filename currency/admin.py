from django.contrib import admin
from .models import Currency

# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CurrencyAdmin(BaseModelAdmin):
    exclude=['slug']
    list_display=['name','code','symbol','factor','is_active']
    search_fields=['name']

admin.site.register(Currency,CurrencyAdmin)