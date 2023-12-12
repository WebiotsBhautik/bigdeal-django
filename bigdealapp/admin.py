from django.contrib import admin
from .models import Banner, BannerType, BannerTheme, Blog,BlogCategory,BlogComment,ContactUs, Coupon, CouponHistory
from django.utils.safestring import mark_safe


# Register your models here.

class BannerAdmin(admin.ModelAdmin):
    exclude = ['slug']
    list_display = ['bannerTheme', 'bannerType', 'bannerProduct']
    ordering = ('bannerTheme','bannerType',)
    # list_per_page=100


admin.site.register(Banner, BannerAdmin)


class BannerTypeAdmin(admin.ModelAdmin):
    exclude = ['slug']


admin.site.register(BannerType, BannerTypeAdmin)


class BannerThemeAdmin(admin.ModelAdmin):
    exclude = ['slug']


admin.site.register(BannerTheme, BannerThemeAdmin)

class BlogCategoryAdmin(admin.ModelAdmin):
    exclude = ['slug']
    list_display=['blog_category_image','categoryName','createdAt']
    ordering=['-createdAt']

    @mark_safe
    def blog_category_image(self, obj):
        return f'<img src="{obj.categoryImage.url}" height="30px" width="30px"/>'
    blog_category_image.short_description = 'Image'


admin.site.register(BlogCategory, BlogCategoryAdmin)


class BlogAdmin(admin.ModelAdmin):
    exclude = ['slug','blogAuthor']
    list_display=['blog_image','blogTitle','blogAuthor','blogCategory','blogStatus','status','createdAt']
    ordering=['-createdAt']

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


class BlogCommentAdmin(admin.ModelAdmin):
    exclude = ['slug']
    list_display=['comment','commentOfBlog','commentByUser','status','createdAt']
    ordering=['-createdAt']

    def get_queryset(self, request):

        if request.user.is_vendor:  
            queryset = super(BlogCommentAdmin, self).get_queryset(request)
            return queryset.filter(commentOfBlog__blogAuthor=request.user)
        else:
        # if request.user.is_superuser:
            queryset = super(BlogCommentAdmin, self).get_queryset(request)
            return queryset

admin.site.register(BlogComment, BlogCommentAdmin)


class ContactUsAdmin(admin.ModelAdmin):
    list_display=['contactUsName','contactUsEmail','contactUsNumber','createdAt']
    ordering=['-createdAt']
        
admin.site.register(ContactUs, ContactUsAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = ['couponCode','couponType','couponDiscountOrFixed','numOfCoupon','minAmount','expirationDateTime','usageLimit','couponDescription','createdAt']
    ordering = ['-createdAt']

admin.site.register(Coupon, CouponAdmin)

class CouponHistoryAdmin(admin.ModelAdmin):
    list_display = ['coupon','couponHistoryByUser','order_id','couponHistoryByOrder']
    ordering = ['-createdAt']
    
    @admin.display(description='Order ID')
    def order_id(self,obj):
        return str(obj.couponHistoryByOrder.id)
    
    @admin.display(description='Order ID')
    def order_id(self,obj):
        return str(obj.couponHistoryByOrder.id)
    
admin.site.register(CouponHistory,CouponHistoryAdmin)
    
    
    


