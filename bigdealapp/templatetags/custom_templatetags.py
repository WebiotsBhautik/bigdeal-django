from urllib.parse import urlencode, urlparse, urlunparse
from django import template
from django.http import QueryDict,HttpResponse

from currency.models import Currency

from order.models import (Cart, CartProducts,Wishlist,Compare)
from product.models import (Product, ProductVariant)
from django.http import QueryDict

from urllib.parse import urlparse, parse_qs, urlencode
import json

# from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID

register = template.Library()


@register.filter(name='to_str')
def to_str(value):
    return str(value)


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='to_int')
def to_int(number):
    return int(number)


@register.filter(name='return_first_product_variant')
def return_first_product_variant(value):
    product = Product.objects.get(id=value)
    productVariant = ProductVariant.objects.filter(variantProduct=product).first()
    if productVariant is not None:
        return productVariant.id
    pass    


@register.filter(name='return_currency_wise_ammount')
def return_currency_wise_ammount(value, request):
    try:
        numeric_value = int(value)
    except ValueError:
        return 0 
    
    result = request.COOKIES.get('currency', '')
    if len(result) == 0:
        currency = Currency.objects.get(code='USD')
        amount = int(value)*currency.factor
        return amount
    
    try:
        currency = Currency.objects.get(id=result)
        amount = numeric_value*currency.factor
    except ObjectDoesNotExist:
        currency = Currency.objects.get(code='USD')
        amount = numeric_value*currency.factor
    return amount


# @register.filter(name='return_currency_wise_ammount_range')
# def return_currency_wise_ammount_range(value, request):
#     result = request.COOKIES.get('currency', '')
#     print('result =======>',result)
    
#     try:
#         uuid_result = UUID(result)
#     except ValueError:
#         print('Invalid UUID, setting default currency')
#         uuid_result = None
    
#     print('uuid_result ======++>',uuid_result)    
#     if uuid_result:
#         try:
#             currency = Currency.objects.get(id=result)
#             print('===> TRY TRY TRY')
#         except ObjectDoesNotExist:
#             print('=====> EXCEPT EXCEPT EXCEPT <======')
#             currency = Currency.objects.get(code='USD')
#     else:
#         print('Invalid UUID, setting default currency')
#         currency = Currency.objects.get(code='USD')
#         print('currency ====>',currency)
        
        
#     productVariantMinPrice = int(value[0])*currency.factor
#     productVariantMaxPrice = int(value[1])*currency.factor
    
#     result_str = str(currency.symbol) + str(productVariantMinPrice)
#     result_str1 = str(currency.symbol) + str(productVariantMaxPrice)
#     print('Result:', result_str)  # Print the result before returning
#     print('result_str1:', result_str1)  # Print the result before returning
    
#     if str(productVariantMinPrice) == str(productVariantMaxPrice):
#         return result_str
#     else:
#         return result_str

    
    
    # if str(productVariantMinPrice) == str(productVariantMaxPrice):
    #     print('AT THE END 1st =====+>')
    #     return str(currency.symbol)+str(productVariantMinPrice)
    # else: 
    #     print('AT THE END 2nd =====+>')
    #     return str(currency.symbol)+str(productVariantMinPrice)
    
    
@register.filter(name='return_currency_wise_ammount_range')
def return_currency_wise_ammount_range(value, request):
    result = request.COOKIES.get('currency', '')
    if len(result) == 0:
        currency = Currency.objects.get(code='USD')
        productVariantMinPrice = int(value[0])*currency.factor
        productVariantMaxPrice = int(value[1])*currency.factor
        if str(productVariantMinPrice) == str(productVariantMaxPrice):
            return str(currency.symbol)+str(productVariantMinPrice)
        else: 
            return str(currency.symbol)+str(productVariantMinPrice)
            
    try:
        currency = Currency.objects.get(id=result)
    except ObjectDoesNotExist:
        currency = Currency.objects.get(code='USD')
    productVariantMinPrice = int(value[0])*currency.factor
    productVariantMaxPrice = int(value[1])*currency.factor
    
    print(str(currency.symbol)+str(productVariantMinPrice))
    print(str(currency.symbol)+str(productVariantMaxPrice))
    
    if str(productVariantMinPrice) == str(productVariantMaxPrice):
        return str(currency.symbol)+str(productVariantMinPrice)
    else:
        return str(currency.symbol)+str(productVariantMinPrice)
        
            


@register.filter(name='return_currency_wise_symbol')
def return_currency_wise_symbol(value, request):
    result = request.COOKIES.get('currency', '')
    if len(result) == 0:
        currency = Currency.objects.get(code='USD')
        return currency.symbol
    try:
        currency = Currency.objects.get(id=result)
    except ObjectDoesNotExist:
        currency = Currency.objects.get(code='USD')  # For example, return USD as a default
    return currency.symbol


@register.filter(name='return_currency_wise_code')
def return_currency_wise_code(value, request):
    result = request.COOKIES.get('currency', '')
    if len(result) == 0:
        currency = Currency.objects.get(code='USD')
        return currency.code
    currency = Currency.objects.get(id=result)
    return currency.code

@register.filter(name='return_currency')
def return_currency(value):
    currency = Currency.objects.all()
    return currency


# Functions to return context for ''''''HEADER'''''' for all pages start

@register.filter(name='return_totalWishlistProducts')
def return_totalWishlistProducts(value,request):
    if request.user.is_authenticated:
        try:
            customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
            wishlist_products = customer_wishlist.wishlistProducts.all()
            totalWishlistProducts = wishlist_products.count()
            return totalWishlistProducts
        except Wishlist.DoesNotExist:
            return 0
    else:
        return 0

@register.filter(name='return_totalComparelistProducts')
def return_totalCompareProducts(value,request):
    if request.user.is_authenticated:
        customer_comparelist = Compare.objects.get(compareByCustomer=request.user.id)
        comparelist_products = customer_comparelist.compareProducts.all()
        totalComparelistProducts = comparelist_products.count()
        return totalComparelistProducts
    else:
        return 0

@register.filter(name='return_totalCartProducts')
def return_totalCartProducts(value,request):
    if request.user.is_authenticated:
        totalCartProducts = CartProducts.objects.filter(cartByCustomer=request.user.id).count()
    else:
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
        else:
            cart_products = None
            
        if cart_products:
            totalCartProducts = len(cart_products)
        else:
            totalCartProducts = 0
    return totalCartProducts

@register.filter(name='return_cart_products')
def return_cart_products(value,request):
    if request.user.is_authenticated:
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    else:
        cart_products = CartProducts.objects.all()
    return cart_products

@register.filter(name='return_cartTotalPrice')
def return_cartTotalPrice(value,request):
    if request.user.is_authenticated:
        try:
            cartTotalPrice = Cart.objects.get(cartByCustomer=request.user.id).getTotalPrice
        except Cart.DoesNotExist:
            return HttpResponse("Cart does not exist for this user 123.")

    else:
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
        else:
            cart_products = None
            
        if cart_products:
                cartTotalPrice = sum([float(i['totalPrice']) for i in cart_products])
        else:
            cartTotalPrice = 0
    return cartTotalPrice

@register.filter(name='return_totalComparelistProducts')
def return_totalCompareProducts(value,request):
    if request.user.is_authenticated:
        customer_comparelist = Compare.objects.get(compareByCustomer=request.user.id)
        comparelist_products = customer_comparelist.compareProducts.all()
        totalComparelistProducts = comparelist_products.count()
        return totalComparelistProducts
    else:
        return 0

# Functions to return context for ''''''HEADER'''''' for all pages end


@register.filter(name='return_selected_attribute_list')
def return_selected_attribute_list(value,request):
    selectedAttributeList = value.split(',')
    selectedAttributeListExcludeLastComma = selectedAttributeList[:-1]
    return selectedAttributeListExcludeLastComma

@register.filter(name='update_url_parameters')
def update_url_parameters(value, request):
    original_string=request.get_full_path()
    
    # Parse the original string
    parsed_url = urlparse(original_string)
    query_params = parse_qs(parsed_url.query)

    # Update the 'page' parameter value
    query_params['page'] = [value]
    
    # Reconstruct the updated query string
    updated_query_string = urlencode(query_params, doseq=True)
    
    # Reconstruct the updated URL
    updated_url = urlunparse(parsed_url._replace(query=updated_query_string))

    # print(updated_url)
    return updated_url


@register.filter
def break_loop(value):
    raise StopIteration









