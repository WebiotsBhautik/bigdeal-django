from django.contrib import admin
from .models import Currency

# Register your models here.

class CurrencyAdmin(admin.ModelAdmin):
    exclude=['slug']
    list_display=['name','code','symbol','factor','is_active']
    search_fields=['name']

admin.site.register(Currency,CurrencyAdmin)