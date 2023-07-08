from django.contrib import admin
from .models import Banner, BannerType, BannerTheme
from django.utils.safestring import mark_safe


# Register your models here.

class BannerAdmin(admin.ModelAdmin):
    exclude = ['slug']
    list_display = ['bannerTheme', 'bannerType', 'bannerProduct']
    ordering = ('bannerTheme','bannerType',)
    list_per_page=10


admin.site.register(Banner, BannerAdmin)


class BannerTypeAdmin(admin.ModelAdmin):
    exclude = ['slug']


admin.site.register(BannerType, BannerTypeAdmin)


class BannerThemeAdmin(admin.ModelAdmin):
    exclude = ['slug']


admin.site.register(BannerTheme, BannerThemeAdmin)

