from django.contrib import admin
from .models import Order,ProductOrder,Cart,Wishlist,Compare,OrderTracking,CartProducts,PaymentMethod,OrderPayment,OrderBillingAddress

from django.urls import reverse
from django.utils.html import format_html

from django.db.models.functions import TruncDay
from django.db.models import Count
# from django.core.serializers.json import DjangoJSONEncoder
import json

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

class OrderAdmin(BaseModelAdmin,admin.ModelAdmin):
    exclude = ['slug','orderedByCustomer','orderPrice','orderSavings','orderTotalPrice']
    list_display=['orderedByCustomer','id','orderTransactionId','orderPrice','orderTotalTax','orderTotalPrice','orderSavings','benefit_amount','final_amount','orderedOrNot','orderCreatedAt']
    ordering=['-orderCreatedAt']
    list_per_page=10
    
    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = super(OrderAdmin, self).get_queryset(request)
            return queryset

    @admin.display(description='Coupon Benefit Amount')
    def benefit_amount(self, obj):
        orderAmount=obj.orderTotalPrice
        orderAmountPayed=obj.orderPayment.orderAmount
        bebefitAmount=orderAmount-orderAmountPayed
        return bebefitAmount
    
    @admin.display(description='Amount')
    def final_amount(self, obj):
        orderAmountPayed=obj.orderPayment.orderAmount
        return orderAmountPayed
    
admin.site.register(Order,OrderAdmin)



class ProductOrderAdmin(BaseModelAdmin,admin.ModelAdmin):

    def get_queryset(self, request):
       
        if request.user.is_vendor:  
            queryset = super(ProductOrderAdmin, self).get_queryset(request)
            return queryset.filter(productOrderedProductsvendor=request.user)
        else:
            queryset = super(ProductOrderAdmin, self).get_queryset(request)
            return queryset

    exclude = ['slug','productOrderedByCustomer','productOrderFinalPrice','productOrderSavings','productOrderTotalPrice','productOrderDiscount']
    list_display=['productOrderedProducts','productOrderOrderId','productOrderPaymentTransactionId','productOrderedByCustomer','productOrderedProductsvendor','productOrderedProductQuantity','productOrderTotalPrice','productOrderSavings','productOrderFinalPrice','productVariantOrderTax','productVariantOrderTaxPrice','productVariantOrderFinalPriceAfterTax','productOrderCreatedAt']
    ordering=['-productOrderCreatedAt']
    list_per_page=10

admin.site.register(ProductOrder,ProductOrderAdmin)

class OrderBillingAddressAdmin(BaseModelAdmin,admin.ModelAdmin):
    list_display=['get_full_name','customerMobile','customerEmail','orderId','orderTransactionId']
    ordering=['-orderBillingAddressCreatedAt']
    list_per_page=10


admin.site.register(OrderBillingAddress,OrderBillingAddressAdmin)

class CartProductAdmin(BaseModelAdmin,admin.ModelAdmin):
    exclude = ['slug']
    list_display=['cart_id','cartByCustomer','cartProduct','cartProductQuantity']


admin.site.register(CartProducts,CartProductAdmin)


class OrderTrackingAdmin(BaseModelAdmin,admin.ModelAdmin):
    exclude=['trackingOrderVendor','trackingOrderCustomer','trackingOrder']
    list_display=['trackingOrderCustomer','trackingOrderVendor','trackingOrderOrderId','trackingOrderOrderTransactionId','getProducts','trackingOrderStatus','trackingModifiedAt']
    search_fields=['trackingOrderCustomer__email','trackingOrderStatus','trackingOrderOrderId']
    list_filter=['trackingOrderCustomer__email','trackingOrderStatus']
    ordering=['-trackingModifiedAt']
    list_per_page=10

    def get_queryset(self, request):

        if request.user.is_vendor:  
            queryset = super(OrderTrackingAdmin, self).get_queryset(request)
            return queryset.filter(trackingOrderVendor=request.user)
        else:  
        # if request.user.is_superuser:
            queryset = super(OrderTrackingAdmin, self).get_queryset(request)
            return queryset

admin.site.register(OrderTracking,OrderTrackingAdmin)


class PaymentMethodAdmin(BaseModelAdmin,admin.ModelAdmin):
    exclude=['slug']
    list_display=['paymentMethodName']
    ordering=['-paymentMethodCreatedAt']

admin.site.register(PaymentMethod,PaymentMethodAdmin)

class OrderPaymentAdmin(BaseModelAdmin,admin.ModelAdmin):
    exclude=['slug']
    list_display=['orderPaymentOrderId','orderPaymentTransactionId','orderPaymentFromCustomer','orderAmount','orderPaymentMethodName','orderPaymentCreatedAt']
    ordering=['-orderPaymentCreatedAt']
    list_per_page=10

    # ,'orderNameOnCard','orderCardNumber','orderExpireationDate','orderCVV'
    
admin.site.register(OrderPayment,OrderPaymentAdmin)
