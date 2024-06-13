from django.contrib import admin
from .models import Banner, BannerType, BannerTheme, Blog,BlogCategory,BlogComment,ContactUs, Coupon, CouponHistory
from django.utils.safestring import mark_safe


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

class BannerAdmin(BaseModelAdmin):
    exclude = ['slug']
    list_display = ['bannerTheme', 'bannerType', 'bannerProduct']
    ordering = ('bannerTheme','bannerType',)
    search_fields = ['bannerTheme__bannerThemeName',]
    # list_per_page=100


admin.site.register(Banner, BannerAdmin)


class BannerTypeAdmin(BaseModelAdmin):
    exclude = ['slug']
    search_fields = ['bannerTypeName',]


admin.site.register(BannerType, BannerTypeAdmin)


class BannerThemeAdmin(BaseModelAdmin):
    exclude = ['slug']
    search_fields = ['bannerThemeName',]


admin.site.register(BannerTheme, BannerThemeAdmin)

class BlogCategoryAdmin(BaseModelAdmin):
    exclude = ['slug']
    list_display=['blog_category_image','categoryName','createdAt']
    ordering=['-createdAt']
    search_fields = ['categoryName',]

    @mark_safe
    def blog_category_image(self, obj):
        return f'<img src="{obj.categoryImage.url}" height="30px" width="30px"/>'
    blog_category_image.short_description = 'Image'


admin.site.register(BlogCategory, BlogCategoryAdmin)


class BlogAdmin(BaseModelAdmin):
    exclude = ['slug','blogAuthor']
    list_display=['blog_image','blogTitle','blogAuthor','blogCategory','blogStatus','status','createdAt']
    ordering=['-createdAt']
    search_fields = ['blogCategory__categoryName','blogTitle']

    def get_queryset(self, request):
       
        if request.user.is_vendor:  
            queryset = super(BlogAdmin, self).get_queryset(request)
            return queryset.filter(blogAuthor=request.user)
        else:
        # if request.user.is_superuser:
            queryset = super(BlogAdmin, self).get_queryset(request)
            return queryset


    @mark_safe
    def blog_image(self, obj):
        return f'<img src="{obj.blogImage.url}" height="30px" width="30px"/>'
    blog_image.short_description = 'Image'
admin.site.register(Blog, BlogAdmin)


class BlogCommentAdmin(BaseModelAdmin):
    exclude = ['slug']
    list_display=['comment','commentOfBlog','commentByUser','status','createdAt']
    ordering=['-createdAt']
    search_fields = ['commentOfBlog__blogTitle','comment']

    def get_queryset(self, request):

        if request.user.is_vendor:  
            queryset = super(BlogCommentAdmin, self).get_queryset(request)
            return queryset.filter(commentOfBlog__blogAuthor=request.user)
        else:
        # if request.user.is_superuser:
            queryset = super(BlogCommentAdmin, self).get_queryset(request)
            return queryset

admin.site.register(BlogComment, BlogCommentAdmin)


class ContactUsAdmin(BaseModelAdmin):
    list_display=['contactUsName','contactUsEmail','contactUsNumber','createdAt']
    ordering=['-createdAt']
    search_fields = ['contactUsName','contactUsNumber']
        
admin.site.register(ContactUs, ContactUsAdmin)


class CouponAdmin(BaseModelAdmin):
    list_display = ['couponCode','couponType','couponDiscountOrFixed','numOfCoupon','minAmount','expirationDateTime','usageLimit','couponDescription','createdAt']
    ordering = ['-createdAt']
    search_fields = ['couponCode','couponType']

admin.site.register(Coupon, CouponAdmin)

class CouponHistoryAdmin(BaseModelAdmin):
    list_display = ['coupon','couponHistoryByUser','order_id','couponHistoryByOrder']
    ordering = ['-createdAt']
    search_fields = ['coupon__couponCode']
    
    @admin.display(description='Order ID')
    def order_id(self,obj):
        return str(obj.couponHistoryByOrder.id)
    
    @admin.display(description='Order ID')
    def order_id(self,obj):
        return str(obj.couponHistoryByOrder.id)
    
admin.site.register(CouponHistory,CouponHistoryAdmin)
    
    
    


