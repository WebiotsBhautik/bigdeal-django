from urllib.parse import urlencode, urlparse, urlunparse
from django import template
from django.http import QueryDict

from currency.models import Currency

# from order.models import (Cart, CartProducts,Wishlist,Compare)
from product.models import (Product, ProductVariant)
from django.http import QueryDict

from urllib.parse import urlparse, parse_qs, urlencode

# from django.core.cache import cache
# from django.core.exceptions import ObjectDoesNotExist

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
    try:
        if len(result) == 0:
            currency = Currency.objects.get(code='USD')
            amount = int(value)*currency.factor
            return amount
        else:
            try:
                currency = Currency.objects.get(id=result)
                amount = int(value)*currency.factor
                return amount
            except Currency.DoesNotExist:
                pass
    except Currency.DoesNotExist:
        pass
        # Currency.objects.all().delete()
        return amount

    # currency = Currency.objects.get(id=result)
    # amount = int(value)*currency.factor
    # return amount


@register.filter(name='return_currency_wise_ammount_range')
def return_currency_wise_ammount_range(value, request):
    result = request.COOKIES.get('currency', '')
    try:
        if len(result) == 0:
            currency = Currency.objects.get(code='USD')
            productVariantMinPrice = int(value[0])*currency.factor
            productVariantMaxPrice = int(value[1])*currency.factor
            if str(productVariantMinPrice) == str(productVariantMaxPrice):
                return str(currency.symbol)+str(productVariantMinPrice)
            else: 
                return str(currency.symbol)+str(productVariantMinPrice) + " - " + str(currency.symbol)+str(productVariantMaxPrice)

        currency = Currency.objects.get(id=result)
        productVariantMinPrice = int(value[0])*currency.factor
        productVariantMaxPrice = int(value[1])*currency.factor
        if str(productVariantMinPrice) == str(productVariantMaxPrice):
            return str(currency.symbol)+str(productVariantMinPrice)
        else:
            return str(currency.symbol)+str(productVariantMinPrice) + " - " + str(currency.symbol)+str(productVariantMaxPrice)
        
    except Currency.DoesNotExist:
        pass
        # Currency.objects.all().delete()



@register.filter(name='return_currency_wise_symbol')
def return_currency_wise_symbol(value, request):
    result = request.COOKIES.get('currency', '')
    try:
        if len(result) == 0:
            currency = Currency.objects.get(code='USD')
            return currency.symbol
        else:
            try:
                currency = Currency.objects.get(id=result)
                return currency.symbol
            except Currency.DoesNotExist:
                pass
    except Currency.DoesNotExist:
        pass
        # Currency.objects.all().delete()
    # return currency.symbol


@register.filter(name='return_currency_wise_code')
def return_currency_wise_code(value, request):
    result = request.COOKIES.get('currency', '')
    try:
        if len(result) == 0:
            currency = Currency.objects.get(code='USD')
            return currency.code
    except Currency.DoesNotExist:
        pass
        # Currency.objects.all().delete()
    currency = Currency.objects.get(id=result)
    return currency.code

@register.filter(name='return_currency')
def return_currency(value):
    currency = Currency.objects.all()
    return currency


# Functions to return context for ''''''HEADER'''''' for all pages start

# @register.filter(name='return_totalWishlistProducts')
# def return_totalWishlistProducts(value,request):
#     if request.user.is_authenticated:
#         customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
#         wishlist_products = customer_wishlist.wishlistProducts.all()
#         totalWishlistProducts = wishlist_products.count()
#         return totalWishlistProducts
#     else:
#         return 0

# @register.filter(name='return_totalComparelistProducts')
# def return_totalCompareProducts(value,request):
#     if request.user.is_authenticated:
#         customer_comparelist = Compare.objects.get(compareByCustomer=request.user.id)
#         comparelist_products = customer_comparelist.compareProducts.all()
#         totalComparelistProducts = comparelist_products.count()
#         return totalComparelistProducts
#     else:
#         return 0

# @register.filter(name='return_totalCartProducts')
# def return_totalCartProducts(value,request):
#     if request.user.is_authenticated:
#         totalCartProducts = CartProducts.objects.filter(cartByCustomer=request.user.id).count()
#     else:
#         get_Item = request.COOKIES.get('cart')
#         cart_products = []
#         if get_Item:
#             try:
#                 cart_products = json.loads(get_Item) 
#             except json.JSONDecodeError as e:
#                 cart_products = []
#         totalCartProducts = len(cart_products)
#     return totalCartProducts

# @register.filter(name='return_cart_products')
# def return_cart_products(value,request):
#     if request.user.is_authenticated:
#         cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
#     else:
#         cart_products = CartProducts.objects.all()
#     return cart_products

# @register.filter(name='return_cartTotalPrice')
# def return_cartTotalPrice(value,request):
#     if request.user.is_authenticated:
#         customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
#         return customer_cart.getTotalPrice
#     else:
#         get_Item = request.COOKIES.get('cart')
#         cart_products = []
#         if get_Item:
#             try:
#                 cart_products = json.loads(get_Item) 
#             except json.JSONDecodeError as e:
#                 cart_products = []
                
#         total_price = 0
        
#         for item in cart_products:
#             price = item.get('totalPrice', 0)
#             quantity = item.get('quantity', 0)
#             total_price += price * quantity
#         return total_price

# @register.filter(name='return_totalComparelistProducts')
# def return_totalCompareProducts(value,request):
#     customer_comparelist = Compare.objects.get(compareByCustomer=request.user.id)
#     comparelist_products = customer_comparelist.compareProducts.all()
#     totalComparelistProducts = comparelist_products.count()
#     return totalComparelistProducts

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









