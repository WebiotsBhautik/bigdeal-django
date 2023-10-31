#  <div class="detail-right">
# <div class="check-price">
# {% if product.productType == "Simple" %} 
# {{""|return_currency_wise_symbol:request}}{{product.product_actual_price_range|return_currency_wise_ammount:request}} 
# {% else %} 
# {{product.product_actual_price_range|return_currency_wise_ammount_range:request}}
# {% endif %}
# </div>
# <div class="price">
# <div class="price">
#     {% if product.productType == "Simple" %}
#     {{""|return_currency_wise_symbol:request}}{{product.product_price_range|return_currency_wise_ammount:request}}
#     {% else %}
#     {{product.product_price_range|return_currency_wise_ammount_range:request}}
#     {% endif %}
# </div>
# </div>
# </div>




#  <h2>{% if banner.bannerProduct.productVariantDiscount|to_int == 0 %}
# {% else %}
# <span class="theme-color">{{banner.bannerProduct.productVariantDiscount}}% OFF</span>
# {% endif %} on all selected product</h2>



# <span class="detail-price">
#                                     {% if product.productType == "Simple" %}
#                                     {{""|return_currency_wise_symbol:request}}{{product.product_price_range|return_currency_wise_ammount:request}}
#                                     {% else %}
#                                     {{product.product_price_range|return_currency_wise_ammount_range:request}}
#                                     {% endif %}
#                                     <del>
#                                        {% if product.productType == "Simple" %} 
#                                        {{""|return_currency_wise_symbol:request}}{{product.product_actual_price_range|return_currency_wise_ammount:request}} 
#                                        {% else %} 
#                                        {{product.product_actual_price_range|return_currency_wise_ammount_range:request}}
#                                        {% endif %}
#                                     </del>
#                                  </span>



from collections import Counter
import decimal
from decimal import Decimal, ROUND_HALF_UP
from django.db.models.deletion import ProtectedError
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder


import json
import uuid

from math import floor
from django.forms import ValidationError
import requests
from datetime import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.models import auth, User
from django.core import serializers,exceptions
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse,Http404

from django.shortcuts import redirect, render, get_object_or_404

from accounts.models import Customer, CustomUser, TemporaryData
from currency.models import Currency
from order.models import (Cart, CartProducts, Compare, Order, OrderTracking,
                          OrderBillingAddress, OrderPayment, PaymentMethod,
                          ProductOrder, Wishlist)

from product.models import (AttributeName, MultipleImages, ProBrand, ProCategory, Product, ProductReview, ProductVariant,AttributeValue,ProductMeta)
from voxoapp.helpers import convert_amount_based_on_currency, get_currency_instance, GetUniqueProducts, IsVariantPresent, GetRoute, create_query_params_url, generateOTP, get_product_attribute_list, get_product_attribute_list_for_quick_view, search_query_params_url

import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import Group
from more_itertools import unique_everseen
from voxoapp.models import Banner, BannerType, BannerTheme, ContactUs, Coupon, CouponHistory
from django.urls import reverse
from django.urls import resolve
from voxoapp.models import Banner, BannerType, BlogCategory, Blog, BlogComment
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Imports For Forgot Password With Email Verification

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str

from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
from django.utils import timezone
import re
from django.db.models import Q,Sum
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    product = ProductOrder.objects.all()
    context = {'product': product}
    return render(request, 'admin/index.html', context)


def set_currency_to_session(request):
    body = json.loads(request.body)
    currencyID = body['currencyId']

    response = HttpResponse('Cookie Set for currency')
    response.set_cookie('currency', currencyID)
    return response

# Home pages section

def get_selected_currency(request):
    currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
    data = {"factor": currency.factor, "symbol": currency.symbol}
    return JsonResponse(data, safe=False)


def setCookie(request):
    response = HttpResponse('Cookie Set')
    response.set_cookie('login_status', True)
    currency = Currency.objects.get(code='USD')
    response.set_cookie('currency', currency.id)
    return response


def signup_page(request):
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['pass']
        cpassword = request.POST['cpass']

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email address is already in use')
        else:
            if password == cpassword:
                if role == 'customer':
                    user = CustomUser.objects.create_user(username=username, email=email, is_customer=True, is_vendor=False, password=password)
                    group = Group.objects.get(name='Customer')
                    user.groups.add(group)
                    user.save()
                    messages.success(request, 'Registration successfully')
                    return redirect('login_page')
                else:
                    user = CustomUser.objects.create_user(
                        username=username, email=email, is_customer=False, is_vendor=True, password=cpassword)
                    group = Group.objects.get(name='Vendor')
                    user.groups.add(group)
                    user.save() 
                    messages.success(request, 'Registration successfully')
                    return redirect('login_page')
            else:
                messages.error(request, 'Password Does Not Match')
                return redirect('signup_page')
        return render(request, 'authentication/sign-up.html')
    else:
        context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"}}
        return render(request, 'authentication/sign-up.html', context)

def add_cart_data_to_database(request,get_Item):
    if (get_Item is not None and get_Item != "null"):
        cart_products = json.loads(get_Item)
    else:
        return False

    for cart_product in cart_products:
        productVariant = ProductVariant.objects.get(id=cart_product['variant_id'])
        if productVariant.productVariantQuantity > 0:
            cartObject=Cart.objects.get(cartByCustomer=request.user)
            if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=productVariant).exists():
                cartProductObject = CartProducts.objects.get(
                    cartByCustomer=request.user, cartProduct=productVariant)
                cartProductObject.cartProductQuantity += int(cart_product['quantity'])
                cartProductObject.save()
            else:
                CartProducts.objects.create(
                    cart=cartObject,cartProduct=productVariant, cartProductQuantity=cart_product['quantity']).save()
        else:
            try:  
                cart = Cart.objects.create(cart_id=_cart_id(request))
            except Cart.DoesNotExist:   
                cart = Cart.objects.create(cart_id=_cart_id(request))

    response = HttpResponseRedirect(reverse('checkout_page'))
    response.delete_cookie('cart')
    return response

def login_page(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['pass']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None and user.is_customer:
            auth.login(request, user)
            response = HttpResponseRedirect('checkout_page')
            cid=Cart.objects.get(cartByCustomer=user)

            response.set_cookie('cid',cid.id)

            get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
            if get_Item:
                if add_cart_data_to_database(request,get_Item):
                    response.delete_cookie('cart')
            currency = Currency.objects.get(code='USD')
            response.set_cookie('currency', currency.id)
            
            return response
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login_page')

    context = {"breadcrumb": {
        "parent": "Dashboard", "child": "Default"}}
    return render(request, 'authentication/log-in.html', context)


def logout_page(request):
    auth.logout(request)
    return redirect('/login_page')


def index_default(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Fashion Demo')
    today = datetime.now()
    
    shop_banners = banners.filter(bannerType__bannerTypeName='Shop Banner')
    first_banner = None
    second_banner = None
    third_banner = None
    fourth_banner = None
    
    
    if shop_banners.count() >= 4:
        first_banner = shop_banners[0]
        second_banner = shop_banners[1]
        third_banner = shop_banners[2]
        fourth_banner = shop_banners[3]
    
    
    fashion_category = ProCategory.objects.get(categoryName='Fashion')
    subcategories = fashion_category.get_descendants(include_self=True)
    fashion_products = Product.objects.filter(proCategory__in=subcategories).order_by('?')
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    template_path = 'pages/home/fashion/fashion.html'

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               "allbanners": banners,
               "Today": today,
               'subcategories':subcategories,
               'fashion_products':fashion_products,
               'products_by_subcategory':products_by_subcategory,
               'first_banner':first_banner,
               'second_banner':second_banner,
               'third_banner':third_banner,
               'fourth_banner':fourth_banner,
               'theme':'Fashion',
               'path':'index_default',
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
               }

    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response
    
    

def get_subcategories(category):
    fashion_category = ProCategory.objects.get(categoryName__iexact=category)
    subcategories = ProCategory.objects.filter(parent=fashion_category)
    
    result = []
    for subcategory in subcategories:
        subcategory_data = {
            'id': subcategory.id,
            'name': subcategory.categoryName,
            'subcategories': get_subcategories(subcategory.categoryName)
        }
        result.append(subcategory_data)
    
    return result



def search_products(request):
    query = request.GET.get('q','')
    category = request.GET.get('category', '') 
   
    products = ProductVariant.objects.all()
   
    if query and category:
        fashion_subcategories = get_subcategories(category)
        category_ids = []
        category_ids.extend(get_category_ids(fashion_subcategories))
        products = products.filter(variantProduct__proCategory__id__in=category_ids, variantProduct__productName__icontains=query)
    else:
        fashion_subcategories = get_subcategories(category)
        category_ids = []
        category_ids.extend(get_category_ids(fashion_subcategories))
        products = ProductVariant.objects.filter(variantProduct__proCategory__id__in=category_ids).order_by('id')[:7]

          
    products = GetUniqueProducts(products)
    results = [{'id': product.variantProduct.id,
                'name': product.variantProduct.productName,
                'price': product.productVariantFinalPrice, 
                'image_url': product.variantProduct.productImageFront.url if product.variantProduct.productImageFront else '',
                'rating': product.variantProduct.productFinalRating,
                'category': product.variantProduct.proCategory.categoryName  
                } for product in products]
    
    return JsonResponse({'status': 200, 'data': results})


def get_category_ids(data):
    category_ids = []
    for category in data:
        category_ids.append(category['id'])
        category_ids.extend(get_category_ids(category['subcategories']))
    return category_ids


def flower_demo(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Flower Demo')
    flower_category = ProCategory.objects.get(categoryName='Flower')
    subcategories = flower_category.get_descendants(include_self=True)
    flower_products = Product.objects.filter(proCategory__in=subcategories)
    most_popular = Product.objects.filter(proCategory__in=subcategories).annotate(total_sold=Sum('productmeta__productSoldQuantity')).order_by('-total_sold')

    
    shop_banners = banners.filter(bannerType__bannerTypeName='Shop Banner')
    first_banner = None
    second_banner = None
    third_banner = None
    fourth_banner = None
    
    
    if shop_banners.count() >= 4:
        first_banner = shop_banners[0]
        second_banner = shop_banners[1]
        third_banner = shop_banners[2]
        fourth_banner = shop_banners[3]

    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Flower',status=True, blogStatus=1)

    cart_products,totalCartProducts = show_cart_popup(request)


    
    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
                'allbanners':banners,
                'subcategories':subcategories,
                'flower_products':flower_products,
                'products_by_subcategory':products_by_subcategory,
                'first_banner':first_banner,
                'second_banner':second_banner,
                'third_banner':third_banner,
                'fourth_banner':fourth_banner,
                'blogs':blogs,
                'theme':'Flower',
                'path':'flower_demo','most_popular':most_popular,
                "cart_products": cart_products,"totalCartProducts": totalCartProducts,

                }
    return render(request, 'pages/home/flower/flower.html', context)


def furniture_demo(request):
    all_banners = BannerTheme.objects.get(bannerThemeName='Furniture Demo')
    banners = Banner.objects.filter(bannerTheme=all_banners)
    furniture_category = ProCategory.objects.get(categoryName='Furniture')
    subcategories = furniture_category.get_descendants(include_self=True)
    furniture_products = Product.objects.filter(proCategory__in=subcategories)
    
    most_popular = Product.objects.filter(proCategory__in=subcategories).annotate(total_sold=Sum('productmeta__productSoldQuantity')).order_by('-total_sold')
    
    
    products_by_subcategory = {}

    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    cart_products,totalCartProducts = show_cart_popup(request)
        
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
                'allbanners':banners,
                'subcategories':subcategories,
                'furniture_products':furniture_products,
                'products_by_subcategory':products_by_subcategory,
                'path':'furniture_demo',
                'theme':'Furniture',
                'most_popular':most_popular,
                "cart_products": cart_products,"totalCartProducts": totalCartProducts,

            }
    return render(request, 'pages/home/furniture/furniture.html', context)


def electronics_demo(request):
    all_banners = BannerTheme.objects.get(bannerThemeName='Electronics Demo')
    banners = Banner.objects.filter(bannerTheme=all_banners)
    insta_banner = banners.filter(bannerType__bannerTypeName='Instagram')

    banner_list = list(Banner.objects.filter(bannerTheme=all_banners, bannerType__bannerTypeName='Banner'))
    electronics_category = ProCategory.objects.get(categoryName='Electronics')
    subcategories = electronics_category.get_descendants(include_self=True)
    electronic_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}

    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'banner_list':banner_list,
               'subcategories':subcategories,
               'electronic_products':electronic_products,
               'products_by_subcategory':products_by_subcategory,
                'theme':'Electronics','insta_banner':insta_banner,
                "cart_products": cart_products,"totalCartProducts": totalCartProducts,

               }
    return render(request, 'pages/home/electronics/electronics.html', context)


def shoes_demo(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Shoes Demo')
    shoes_category = ProCategory.objects.get(categoryName='Shoes')
    subcategories = shoes_category.get_descendants(include_self=True)
    shoes_products = Product.objects.filter(proCategory__in=subcategories)
    
    shop_banners = banners.filter(bannerType__bannerTypeName='Shop Banner').order_by('-id')[:4]
    
    first_banner = None
    second_banner = None
    third_banner = None
    fourth_banner = None
    
    if shop_banners.count() >= 4:
        first_banner = shop_banners[0]
        second_banner = shop_banners[1]
        third_banner = shop_banners[2]
        fourth_banner = shop_banners[3]
    

    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
                'allbanners':banners,
                'first_banner':first_banner,
                'second_banner':second_banner,
                'third_banner':third_banner,
                'fourth_banner':fourth_banner,
                'subcategories':subcategories,
                'shoes_products':shoes_products,
                'products_by_subcategory':products_by_subcategory,
                'theme':'Shoes',
                "cart_products": cart_products,"totalCartProducts": totalCartProducts,
               }
    return render(request, 'pages/home/shoes/shoes.html', context)


def vegetables_demo(request):
    all_banners = Banner.objects.filter(bannerTheme__bannerThemeName='Vegetable Demo')
    banner_list = list(Banner.objects.filter(bannerTheme__bannerThemeName='Vegetable Demo', bannerType__bannerTypeName='Banner'))

    vegetable_category = ProCategory.objects.get(categoryName='Vegetable')
    subcategories = vegetable_category.get_descendants(include_self=True)
    vegetable_products = Product.objects.filter(proCategory__in=subcategories)

    products_by_subcategory = {}

    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
    blogs = Blog.objects.filter(blogCategory__categoryName='Vegetable',status=True, blogStatus=1)

    cart_products,totalCartProducts = show_cart_popup(request)
    

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'all_banners':all_banners,
               'banner_list':banner_list,
               'subcategories':subcategories,
               'vegetable_products':vegetable_products,
               'products_by_subcategory':products_by_subcategory,
               'blogs':blogs,'theme':'Vegetable',
               'path':'vegetables_demo',
               "cart_products": cart_products,"totalCartProducts": totalCartProducts,
               }
    return render(request, 'pages/home/vegetables/vegetables.html', context)


# Shop pages section


def canvas_filter(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    
    
    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    rating_range = ['1', '2', '3', '4', '5']
    categoryid = ()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))
        url = reverse('canvas_filter_with_id', args=[id])
        


    if selected_allprice:
        price = selected_allprice.split(',')

        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)
            
            

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]
            product = ProductVariant.objects.filter(variantProduct__productBrand__brandName__in=brands)
    
    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1
     

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    paginator = Paginator(product,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    totalProduct = len(product)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
    if product and selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
    cart_products,totalCartProducts = show_cart_popup(request)
    

    context = {"breadcrumb": {"parent": "Shop Canvas Filter", "child": "Canvas Filter"},
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'shop_banner':shop_banner,
            'categoryid':categoryid,
            'url':url,
            'rating_range':rating_range,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'canvas_filter',
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'totalProduct':totalProduct,
            
            }
    
    return render(request,'pages/shop/canvas-filter.html', context)


def category_filter(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))

    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))


    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    categoryid = ()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('category_filter_with_id', args=[id])

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)

    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor,Decimal(price[1])/factor))
        

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]

        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]
            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)
            
    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)

    product = GetUniqueProducts(product)
    paginator = Paginator(product,15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
 
    context = {"breadcrumb": {"parent": "Shop Category Filter", "child": "Category Filter"},
           'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,'rating_range':rating_range,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'url':url,"path":'category_filter',
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'categoryid':categoryid,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            }
    return render(request, 'pages/shop/shop-category-slider.html',context)


def filter_hide(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    max_price = []
    min_price = []
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))


    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('filter_hide_with_id', args=[id])

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)

    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]
            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1
     

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
    

    product = GetUniqueProducts(product)
    paginator = Paginator(product,12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb":{"parent":"Shop Filter Hide","child": "Filter Hide"},
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,'discount_filters':discount_filters,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'rating_range':rating_range,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_discounts':selected_alldiscount,
            'url': url,'page_obj':page_obj,
            'path':'filter_hide',
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,

}
    
    return render(request, 'pages/shop/shop-filter-hide.html',context)


def shop_left_slidebar(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))


    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    categoryid = ()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_left_slidebar_with_id', args=[id])

    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product
        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product=ProductVariant.objects.filter(variantProduct__productBrand__brandName__in=brands)
            
  
        
    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)


    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1
     

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            

    product = GetUniqueProducts(product)
    paginator = Paginator(product,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    
    context = {"breadcrumb": {"parent": "Shop Left Slidebar", "child": "Left Slidebar"},
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'shop_banner':shop_banner,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'categoryid':categoryid,'rating_range':rating_range,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'shop_left_slidebar','url':url,
            'page_obj':page_obj,'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request,'pages/shop/shop-left-slidebar.html', context)


def list_infinite(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    categoryid = ()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('list_infinite_with_id', args=[id])

    if selected_allprice:

        price = selected_allprice.split(',')

        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor


        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]

        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)


    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)

    product = GetUniqueProducts(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    
    context = {"breadcrumb":{"parent":"Shop List Infinite","child": "List Infinite"},
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'ProductsBrand': brand, 'ProductCategory': category,
            'shop_banner':shop_banner,'products': product,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'url':url,'productVariant':product,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'list_infinite','rating_range':rating_range,
            'page_obj':page_obj,'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request, 'pages/shop/shop-list-infinite.html', context)


def shop_list(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))

    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []


    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_list_with_id', args=[id])

    if selected_allprice:

        price = selected_allprice.split(',')

        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            scol = request.GET['colors'] if 'colors' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)

    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)

    product = GetUniqueProducts(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb":{"parent":"Shop List","child": "List"},
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'shop_banner':shop_banner,
            'rating_range':rating_range,'url':url,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'shop_list','page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request, 'pages/shop/shop-list.html',context)


def shop_no_sidebar(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_no_sidebar_with_id', args=[id])

    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1
     

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)


    product = GetUniqueProducts(product)
    paginator = Paginator(product,15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb":{"parent":"Shop No Sidebar","child": "No Sidebar"},
             'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'url':url,
            'rating_range':rating_range,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            "path":'shop_no_sidebar',
            'page_obj':page_obj,'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request, 'pages/shop/shop-no-sidebar.html',context)


def shop_right_sidebar(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    categoryid = ()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_right_sidebar_with_id', args=[id])

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)

    if selected_allprice:
        price = selected_allprice.split(',')

        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)


    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)

    product = GetUniqueProducts(product)
    
    paginator = Paginator(product,12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb":{"parent":"Shop Right Sidebar","child": "Right Sidebar"},
            'productVariant':product,'products':product,
            'ProductsBrand':brand,'ProductCategory': category,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'shop_banner':shop_banner,
            'url':url,'rating_range':rating_range,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'shop_right_sidebar','page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request, 'pages/shop/shop-right-sidebar.html',context)


def shop_top_filter(request, category_id=None):
    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_top_filter_with_id', args=[id])

    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            scol = request.GET['colors'] if 'colors' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]

            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)


    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)

    product = GetUniqueProducts(product)
    paginator = Paginator(product,12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)
            
    context = {"breadcrumb":{"parent": "Shop Top Filter","child": "Top Filter"},
            'ProductsBrand': brand, 'ProductCategory': category,
            'products': product,'rating_range':rating_range,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'url':url,'productVariant':product,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'shop_top_filter','page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,

            }
    return render(request, 'pages/shop/shop-top-filter.html',context)


def shop_with_category(request, category_id=None):

    url = ''
    discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]

    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []
    selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
    selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = min(list(get_all_prices))
    max_price = max(list(get_all_prices))
    
    selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))

    
    attributeNameList=[]
    attributeDictionary={}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()

    product = ProductVariant.objects.all()
    rating_range = ['1', '2', '3', '4', '5']
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()

    if category_id:
        categoryid = ProCategory.objects.get(id=category_id)
        product = ProductVariant.objects.filter(
            variantProduct__proCategory=categoryid)

        brandList = []
        brand = []

        for p in product:
            brandList.append(str(p.variantProduct.productBrand.brandName))

        for b in list(set(brandList)):
            brand.append(ProBrand.objects.get(brandName=b))

        url = reverse('shop_with_category_with_id', args=[id])

    if selected_allprice:
        price = selected_allprice.split(',')

        price_filter = product
        
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor

        product = price_filter.filter(
            productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]

        product = []
        for brands in y:
            product1 = brand_filter.filter(
                variantProduct__productBrand__brandName=brands)
            product += product1

    if selected_alldiscount:
        x = selected_alldiscount.split(',')
        select_disc = x[:-1]
        discount_filter = product

        if len(discount_filter) and type(discount_filter) is not list:
            product = discount_filter.filter(
                productVariantDiscount__gte=select_disc[0])
        else:
            sbd = request.GET['brands'] if 'brands' in request.GET else []
            spri = request.GET['price'] if 'price' in request.GET else []
            sdis = request.GET['discount'] if 'discount' in request.GET else []

            x = sbd.split(",")
            y = x[:-1]
            brands = [s.strip('"') for s in y]
            product = ProductVariant.objects.filter(
                variantProduct__productBrand__brandName__in=brands)

    if selected_rating:
        rating = selected_rating.rstrip(',')
        rating_filter = product
        if len(rating_filter):
            product = rating_filter.filter(
                variantProduct__productFinalRating=rating)


    if attributeDictionary:
        for attribute in attributeNameList:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]  
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                x = attributeDictionary[attribute].split(',')
                y = x[:-1]
                product = []
                for values in y:
                    attributeNameObj=AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
                    product += product1


    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            

    product = GetUniqueProducts(product)
    paginator = Paginator(product,12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filter product count
    totalProduct = len(product)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    
    
    context = {"breadcrumb":{"parent": "Shop With Category","child": "With Category"},
            'productVariant':product,
            'shop_banner':shop_banner,'rating_range':rating_range,
            'ProductsBrand':brand,'ProductCategory': category,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,
            'products':product,'url':url,
            'discount_filters':discount_filters,
            'select_brands':selected_allbrand,
            'selected_prices':selected_allprice,
            'selected_discounts':selected_alldiscount,
            'path':'shop_with_category','page_obj':page_obj,
            'attributeDict':attributeDict,'totalProduct':totalProduct,
            'min_price':min_price*selected_currency.factor,
            'max_price':max_price*selected_currency.factor,
            'symbol':selected_currency.symbol,
            }
    return render(request, 'pages/shop/shop-with-category.html',context)


# ======> Product pages section <========

def image_4(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(
        proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None

    if request.user.is_authenticated:    
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus = False
    
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)


    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    
    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Product 4 Images", "child": "Product 4 Images"},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "cart_products_demo": cart_products_demo,
               "product": product, "products": products,
               "productVariants": productVariants,
                "firstProductVariant": str(firstProductVariant),
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "related_products": related_products,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
                'attributeDict':attributeDict,

               }
    return render(request, 'pages/product/image_4.html', context)


def left_slidebar(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None
        
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    cart_products,totalCartProducts = show_cart_popup(request)
        
    context = {"breadcrumb": {"parent": "Product Left Slidebar", "child": "Product Left Slidebar"},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "cart_products_demo": cart_products_demo,
               "product": product, "products": products,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "related_products": related_products,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }
    return render(request, 'pages/product/product-left-slidebar.html', context)


def get_product_variant(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        productId = body['productId']
        selectedAttributeValueDict = body['selectedAttributeValueDict']
        product = Product.objects.get(id=str(productId))
        try:
            selectedAttribute=[]    
            for value in selectedAttributeValueDict:
                selectedAttribute.append(AttributeValue.objects.get(attributeValue=selectedAttributeValueDict[value]))
            productVariants=ProductVariant.objects.filter(variantProduct=product)
            for productVariant in productVariants:
                productVariantAttributes=productVariant.productVariantAttribute.all()
                attributeList1 = Counter(list(productVariantAttributes))
                attributeList2 = Counter(selectedAttribute)
                if attributeList1 == attributeList2:
                    productVariantId= productVariant.id,
                    productVariantPrice= productVariant.productVariantFinalPrice,
                    productVariantDiscount= productVariant.productVariantDiscount,
                    productVariantActualPrice= productVariant.productVariantPrice,
                    productVariantQuantity= productVariant.productVariantQuantity
                    break        
            
            data = {
                "productVariantId": productVariantId,
                "productVariantPrice": productVariantPrice,
                "productVariantDiscount": productVariantDiscount,
                "productVariantActualPrice": productVariantActualPrice,
                "productVariantQuantity": productVariantQuantity
            }
            return JsonResponse(data, safe=False)
        except:
            data = {
                "productVariantId": "No Product Yet",
                "productVariantPrice": "Product Out Of Stock",
            }
            return JsonResponse(data, safe=False)


def product_360_view(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    
    try:
        product = Product.objects.get(id=id)
    except(ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()

    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(
        proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()

    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
        
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {"breadcrumb": {"parent": "Product 360 View", "child": "Product 360 View"},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "cart_products_demo": cart_products_demo,
               "product": product, "products": products,
               "productVariants": productVariants,
                "firstProductVariant": str(firstProductVariant),
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "related_products": related_products,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }
    return render(request, 'pages/product/product-360-view.html', context)


def bundle(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
  
    try:
        product = Product.objects.get(id=id)
    except(ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(
        proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break   
    else:
        reviewStatus =False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {"breadcrumb": {"parent": "Product Bundle", "child": "Product Bundle"},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "cart_products_demo": cart_products_demo,
               "product": product, "products": products,
               "productVariants": productVariants,
                "firstProductVariant": str(firstProductVariant),
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "related_products": related_products,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }

    return render(request, 'pages/product/product-bundle.html', context)


def left_thumbnail(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
   
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(
        proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant  = None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus = False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    

    context = {"breadcrumb": {"parent": "Product Left Thumbnail", "child": "Product Left Thumbnail"},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "cart_products_demo": cart_products_demo,
               "product": product, "products": products,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "related_products": related_products,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }

    return render(request, 'pages/product/product-left-thumbnail.html', context)


def product_no_sidebar(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()

    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(
        proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    
    cart_products,totalCartProducts = show_cart_popup(request)




    context = {"breadcrumb": {"parent": "Product No Sidebar", "child": "Product No Sidebar"},
               "product": product, "products": products,
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
                "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "related_products": related_products,
                "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }

    return render(request, 'pages/product/product-no-sidebar.html', context)


def product_right_slidebar(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    totalCartProducts = cart_products.count()
    
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant=None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    
    cart_products,totalCartProducts = show_cart_popup(request)


    

    context = {"breadcrumb": {"parent": "Product Right Slidebar", "child": "Product Right Slidebar"},
               "product": product, "products": products,
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               }

    return render(request, 'pages/product/product-right-sidebar.html', context)


def right_thumbnail(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                
    else:
        reviewStatus=False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    
    cart_products,totalCartProducts = show_cart_popup(request)


    

    context = {"breadcrumb": {"parent": "Product Right Thumbnail", "child": "Product Right Thumbnail"},
               "product": product, "products": products,
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               }

    return render(request, 'pages/product/product-right-thumbnail.html', context)


def sticky(request, id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize(
        "json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    products = ProductVariant.objects.all()
    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    related_products = Product.objects.filter(proCategory=product.proCategory).exclude(id=product.id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
        
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)
    
    
    cart_products,totalCartProducts = show_cart_popup(request)

    
    context = {"breadcrumb": {"parent": "Product Sticky", "child": "Product Sticky"},
        "cart_products": cart_products, "totalCartProducts": totalCartProducts,
        "product": product,"products": products,
        "productVariants": productVariants,
        "firstProductVariant":str(firstProductVariant),
        "attributeObjects":attributeObjects,
        "attributeObjectsIds":attributeObjectsIds,
        "images": images,
        "ProductsBrand": brand,
        "ProductCategory": category,
        "related_products": related_products,
        "customerReviews":customerReviews,
        "ratingPercentage":ratingPercentage,
        "average_rating":average_rating,
        "rating_range":rating_range,
        "reviewStatus":reviewStatus,
        }
    
    return render(request, 'pages/product/product-sticky.html', context)

def video_thumbnail(request,id):
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    totalCartProducts = cart_products.count()
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    
    products = ProductVariant.objects.all()


    images = MultipleImages.objects.filter(multipleImageOfProduct=product)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
    firstProductVariant = ProductVariant.objects.filter(
        variantProduct=product).first()
    if firstProductVariant:
        firstProductVariant = firstProductVariant.id
    else:
        firstProductVariant = None
        
    if request.user.is_authenticated:
        customer=CustomUser.objects.get(id=request.user.id)
        productOrders=ProductOrder.objects.filter(productOrderedByCustomer=customer)
        reviewStatus=False
        for proOrder in productOrders:
            if proOrder.productOrderedProducts.variantProduct== product:
                reviewStatus=True
                break
    else:
        reviewStatus=False
  
    customerReviews = ProductReview.objects.filter(productName__id=id)

    total_review_count = customerReviews.count()
    if total_review_count > 0:
        total_rating = sum([int(review.productRatings) for review in customerReviews])
        average_rating = round(total_rating / total_review_count)   
    else:
        average_rating = 0
    rating_range = ['1', '2', '3', '4', '5']

    totalReviewCount = product.productNoOfReview
    oneStarcount = ProductReview.objects.filter(
        productName=product, productRatings="1").count()
    twoStarcount = ProductReview.objects.filter(
        productName=product, productRatings="2").count()
    threeStarcount = ProductReview.objects.filter(
        productName=product, productRatings="3").count()
    fourStarcount = ProductReview.objects.filter(
        productName=product, productRatings="4").count()
    fiveStarcount = ProductReview.objects.filter(
        productName=product, productRatings="5").count()

    if totalReviewCount > 0:
        ratingPercentage = {
            "one_stars": Decimal((oneStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "two_stars": Decimal((twoStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "three_stars": Decimal((threeStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "four_stars": Decimal((fourStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
            "five_stars": Decimal((fiveStarcount/totalReviewCount)*100).quantize(Decimal('.1'), rounding=ROUND_HALF_UP),
        }
        total = sum(ratingPercentage.values())
        last_number = Decimal(
            100 - total + ratingPercentage['five_stars']).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        ratingPercentage['five_stars'] = last_number
        total = sum(ratingPercentage.values())
        assert total == 100

    else:
        ratingPercentage = {
            "one_stars": "0",
            "two_stars": "0",
            "three_stars": "0",
            "four_stars": "0",
            "five_stars": "0"
        }
        
    attributeObjects, attributeObjectsIds = get_product_attribute_list(id)

    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    
    
    cart_products,totalCartProducts = show_cart_popup(request)
    

    context = {"breadcrumb": {"parent": "Product Video Thumbnail", "child": "Product Video Thumbnail"},
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "product": product, "products": products,
               "productVariants": productVariants,
               "firstProductVariant": str(firstProductVariant),
               "images": images,
               "ProductsBrand": brand,
               "ProductCategory": category,
               "attributeObjects":attributeObjects,
               "attributeObjectsIds":attributeObjectsIds,
               "customerReviews":customerReviews,
               "ratingPercentage":ratingPercentage,
               "average_rating":average_rating,
               "rating_range":rating_range,
               "reviewStatus":reviewStatus,
               }
    
    return render(request, 'pages/product/product-video-thumbnail.html', context)


# ========>  Pages Section <==========

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, id=None, quantity=0):
    productVariant = ProductVariant.objects.get(id=id)
    cart_item = {
        'product_id': str(productVariant.variantProduct.id),
        'variant_id': id,
        'quantity': quantity,
        'productImage' : productVariant.variantProduct.productImageFront.url,
        'productName' : productVariant.variantProduct.productName,
        'price': productVariant.productVariantFinalPrice,
        
    }
    
    cart_item['totalPrice'] = format(int(cart_item['quantity']) * cart_item['price'],".2f")  # Calculate total price
    current_user = request.user
    if current_user.is_authenticated:
        if productVariant.productVariantQuantity > 0:
            cartObject=Cart.objects.get(cartByCustomer=request.user)
            if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=productVariant).exists():
                cartProductObject = CartProducts.objects.get(
                    cartByCustomer=request.user, cartProduct=productVariant)
                cartProductObject.cartProductQuantity += int(quantity)
                cartProductObject.save()
                return redirect(request.META['HTTP_REFERER'])
            else:
                CartProducts.objects.create(
                    cart=cartObject,cartProduct=productVariant, cartProductQuantity=quantity).save()
                return redirect(request.META['HTTP_REFERER'])
        else:
            try:  
                cart = Cart.objects.create(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
    else:
        cart_items= []
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
        updated = False

        if (get_Item is not None and get_Item != "null"):
            cart_items = json.loads(get_Item)
            # Check if the item already exists in the cart_items list and update quantity
            for cart_item_cookie in cart_items:

                if cart_item_cookie['product_id'] == str(productVariant.variantProduct.id) and cart_item_cookie['variant_id'] == str(id):
                    cart_item_cookie['quantity'] = int(cart_item_cookie['quantity']) + 1
                    updated = True
                    break

            if not updated:
                cart_items.append(cart_item)
                updated = True

        if not updated:
            cart_items.append(cart_item)
        cart_items_json = json.dumps(cart_items)

        response = HttpResponseRedirect(reverse('index_default'))
        response.set_cookie('cart', cart_items_json)
        return response
        
            
def get_total_tax_values(variant_products):
    TotalVariantTax = 0
    TotalVariantTaxPrice = 0
    TotalVariantFinalPriceAfterTax = 0

    for variant_product in variant_products:
        variant = ProductVariant.objects.get(id = variant_product['variant_id'])
        TotalVariantTax += variant.productVariantTax * int(variant_product['quantity'])
        TotalVariantTaxPrice += variant.productVariantTaxPrice * int(variant_product['quantity'])
        TotalVariantFinalPriceAfterTax += variant.productVariantFinalPriceAfterTax * int(variant_product['quantity'])
        
    return TotalVariantTax,TotalVariantTaxPrice,TotalVariantFinalPriceAfterTax

@csrf_exempt
def add_to_cart_product_quantity_management(request, id, actionType):
    if request.user.is_authenticated:
        productVariant = ProductVariant.objects.get(id=id)
        cart = Cart.objects.get(cartByCustomer=request.user)

        if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=productVariant).exists():
            cartProductObject = CartProducts.objects.get(cartByCustomer=request.user, cartProduct=productVariant)

            if actionType == "plus":
                if productVariant.productVariantQuantity > 0:
                    cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + 1
                    cartProductObject.save()
                    cartTotalPrice = cart.getTotalPrice
                    cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
                    data = {
                        "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
                        "cartTotalPrice": cartTotalPrice,
                        "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
                        "taxPrice":cart.getTotalTax
                    }
                    return JsonResponse(data, safe=False)
                else:
                    cartTotalPrice = cart.getTotalPrice
                    cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
                    data = {
                        "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
                        "cartTotalPrice": cartTotalPrice,
                        "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
                        "taxPrice":cart.getTotalTax
                    }
                    return JsonResponse(data, safe=False)

            if actionType == "minus":
                cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity - 1
                cartProductObject.save()
                cartTotalPrice = cart.getTotalPrice
                cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
                data = {
                    "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
                    "cartTotalPrice": cartTotalPrice,
                    "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
                    "taxPrice":cart.getTotalTax
                }
                return JsonResponse(data, safe=False)
            
    else:
        productVariant = ProductVariant.objects.get(id=id)
        product_id = productVariant.variantProduct.id
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None

        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
        else:
            cart_products = []

        if actionType == "plus" and cart_products:

            for item in cart_products:
                if str(id) == item['variant_id'] and str(product_id) == item['product_id']:
                    item['quantity'] = int(item['quantity']) + 1
                    item['totalPrice'] = format(item['quantity'] * item['price'],".2f")

        if actionType == "minus" and cart_products:
            for item in cart_products:
                if str(id) == item['variant_id'] and str(product_id) == item['product_id']:
                    if item['quantity'] >= 1:
                        item['quantity'] -= 1
                        item['totalPrice'] = format(item['quantity'] * item['price'],".2f")
                    else:
                        cart_products = [item for item in cart_products if item.get('product_id') != id]
                        break
        res_data = [item for item in cart_products if str(id) == item.get('variant_id') and str(product_id) == item.get('product_id')]
        TotalPrice = sum([float(i['totalPrice']) for i in cart_products])
        TotalTax,TotalTaxPrice,TotalFinalPriceAfterTax = get_total_tax_values(cart_products)
        
        data = {
                    "quantityTotalPrice": res_data[0]['totalPrice'],
                    "cartTotalPrice": TotalPrice,
                    "cartTotalPriceAfterTax": TotalFinalPriceAfterTax,
                    "taxPrice":TotalTaxPrice,
                }

        response = JsonResponse(data,safe=False)
        response.set_cookie('cart', cart_products)
        return response
              


def cart_page(request,cart_products=None):
    current_user = request.user
    customer_cart = request.user
    totalCartProducts = 0
    cartTotalPriceAfterTax = 0
    cart_products = []
    
    context = {"breadcrumb": {"parent": "Shopping Cart", "child": "Cart"},
               }

    if current_user.is_authenticated:
        try:
            customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        except Cart.DoesNotExist:
            customer_cart = Cart.objects.create(cartByCustomer=request.user)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()
        cartTotalPriceAfterTax = customer_cart.getFinalPriceAfterTax
        context["cartId"]=customer_cart.id,
    else:
        try:  
            customer_cart = Cart.objects.create(cart_id=_cart_id(request))
        except Cart.DoesNotExist:   
            customer_cart = Cart.objects.create(cart_id=_cart_id(request))
            
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
        if get_Item:
            cart_products = json.loads(get_Item)  # Default to an empty list if no data
            
            for item in cart_products:
                item['totalPrice'] = int(item['quantity']) * float(item['price'])

        totalCartProducts = len(cart_products)
        TotalTax,TotalTaxPrice,cartTotalPriceAfterTax = get_total_tax_values(cart_products)
        TotalPrice = sum([float(i['totalPrice']) for i in cart_products])
        context["cartTotalPrice"]=TotalPrice
        context["cartTotalTax"]=TotalTaxPrice
        cartTotalPriceAfterTax = TotalPrice + TotalTaxPrice


    
    context["cart_products"]= cart_products
    context["totalCartProducts"]= totalCartProducts
    context["cartTotalPriceAfterTax"]= cartTotalPriceAfterTax
    context["Cart"]= customer_cart
    context["cartId"]=customer_cart.id

    return render(request, 'pages/pages/cart.html', context)


def delete_cart_product(request, id):
    if request.user.is_authenticated:
        CartProducts.objects.filter(cartProduct=id).delete()
    else:
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None

        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
        else:
            cart_products = []

        if len(cart_products) >= 1:
            
            cart_products = [item for item in cart_products if item.get('variant_id') != str(id)]
            response = HttpResponseRedirect(reverse('cart_page'))
            response.set_cookie('cart', cart_products)
            return response
    return redirect('cart_page')


def delete_cart_product_form_header_button(request, id):
    if request.user.is_authenticated:
        CartProducts.objects.filter(cartProduct=id).delete()
    else:
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None

        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
        else:
            cart_products = []

        if len(cart_products) >= 1:
            cart_products = [item for item in cart_products if item.get('variant_id') != str(id)]
            response = HttpResponseRedirect(reverse('cart_page'))
            response.set_cookie('cart', cart_products)
            return response
    return redirect('index_default')


def delete_cart_all_product(request):
    if request.user.is_authenticated:
        CartProducts.objects.filter(cartByCustomer=request.user.id).delete()
    else:
        get_cookie = request.COOKIES.get('cart')
        if get_cookie:
            response = HttpResponseRedirect(reverse('cart_page'))
            response.delete_cookie('cart')
            return response
    return redirect('cart_page')


@login_required(login_url='login_page')
def cart_to_checkout_validation(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            body = json.loads(request.body)
            cartId = body["cartId"]
            cart = Cart.objects.get(id=cartId)
            cartProducts = CartProducts.objects.filter(cart=cart)
            productList = []
            flag = False
            for product in cartProducts:
                dbProduct=ProductVariant.objects.get(id=product.cartProduct.id)
                if product.cartProductQuantity <= dbProduct.productVariantQuantity:
                    pass
                else:
                    productList.append({"productName":str(product.cartProduct.variantProduct.productName),"outOfStockProducts":str(product.cartProduct.productVariantQuantity)})
            if len(productList) > 0:
                flag=True
            
            if flag:
                data={"outOfStockProducts":productList,"flag":str(flag),}
                response = JsonResponse(data,safe=False)
                expiry_time = datetime.utcnow() + timedelta(seconds=30)
                response.set_cookie('checkout', 'False',expires=expiry_time)
                return response
            else:
                data={"outOfStockProducts":productList,"flag":str(flag),}
                response = JsonResponse(data,safe=False)
                expiry_time = datetime.utcnow() + timedelta(seconds=30)
                response.set_cookie('checkout', 'True',expires=expiry_time)
                return response
    else:
        return redirect('login_page')

def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        customer_wishlist = Wishlist.objects.get(
            wishlistByCustomer=request.user.id)
        customer_wishlist.wishlistProducts.add(id)
        customer_wishlist.save()
    else:
        return redirect('login_page')
    return redirect(request.META['HTTP_REFERER'])


def wishlist_page(request):
    totalCartProducts = 0
    wishlist_products = None
    totalWishlistProducts = 0
    if request.user.is_authenticated:
        customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()

        customer_wishlist = Wishlist.objects.get(
            wishlistByCustomer=request.user.id)
        wishlist_products = customer_wishlist.wishlistProducts.all()
        wishlist_product = customer_wishlist.wishlistProducts.first()

        totalWishlistProducts = wishlist_products.count()
    else:
        return redirect('login_page')

    context = {"breadcrumb": {"parent": "Wishlist", "child": "Wishlist"},
               "totalCartProducts": totalCartProducts,
               "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts, }

    return render(request, 'pages/pages/wishlist.html', context)


def delete_wishlist_product(request, id):
    customer_wishlist = Wishlist.objects.get(
        wishlistByCustomer=request.user.id)
    customer_wishlist.wishlistProducts.remove(id)
    customer_wishlist.save()
    return redirect('wishlist_page')


def add_to_cart_from_wishlist(request, id, quantity):
    product = ProductVariant.objects.get(id=id)
    cartObject=Cart.objects.get(cartByCustomer=request.user.id)

    if product.productVariantQuantity > 0:
        if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=product).exists():
            cartProductObject = CartProducts.objects.get(cartByCustomer=request.user, cartProduct=product)
            cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + int(quantity)
            cartProductObject.save()

            # Product remove from wishlist
            customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
            customer_wishlist.wishlistProducts.remove(id)
            customer_wishlist.save()
            return redirect('wishlist_page')
        else:
            CartProducts.objects.create(
                cart=cartObject,cartProduct=product, cartProductQuantity=quantity).save()

            # Product remove from wishlist
            customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
            customer_wishlist.wishlistProducts.remove(id)
            customer_wishlist.save()
            return redirect('wishlist_page')
    else:
        messages.success(request, 'Product out of stock.')
        return redirect('wishlist_page')


def compare_page(request):
    if request.user.is_authenticated:
        customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()

        customer_wishlist = Wishlist.objects.get(
            wishlistByCustomer=request.user.id)
        wishlist_products = customer_wishlist.wishlistProducts.all()
        totalWishlistProducts = wishlist_products.count()

        customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
        compare_products = customer_compare.compareProducts.all()
    else:
        return redirect('login_page')

    context = {"breadcrumb": {"parent": "Compare", "child": "Compare"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "compare": customer_compare, "compare_products": compare_products}
    return render(request, 'pages/pages/compare.html', context)


def compare_products(request, id):
    if request.user.is_authenticated:
        customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
        customer_compare.compareProducts.add(id)
        customer_compare.save()
        return HttpResponse(status=204)
    else:
        return redirect('login_page')
    return redirect(request.META['HTTP_REFERER'])


def add_to_cart_from_compare(request, id, quantity):
    # Compare product added from compare to cart
    product = ProductVariant.objects.get(id=id)

    if product.productVariantQuantity > 0:
        if request.user.is_authenticated:
            cartObject=Cart.objects.get(cartByCustomer=request.user.id)
            if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=product).exists():
                cartProductObject = CartProducts.objects.get(cartByCustomer=request.user, cartProduct=product)
                cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + int(quantity)
                cartProductObject.save()

                # Compare product removed compare
                customer_compare = Compare.objects.get(
                    compareByCustomer=request.user.id)
                customer_compare.compareProducts.remove(id)
                customer_compare.save()
                return redirect('compare_page')

            else:
                CartProducts.objects.create(
                    cart=cartObject,cartProduct=product, cartProductQuantity=quantity).save()
                # Compare product removed compare
                customer_compare = Compare.objects.get(
                    compareByCustomer=request.user.id)
                customer_compare.compareProducts.remove(id)
                customer_compare.save()
                return redirect('compare_page')
    else:
        messages.success(request, 'Product out of stock.')
        return redirect('compare_page')


@csrf_exempt
def quick_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)

        productId = body["productId"]
        productVariantId = body["productVariantId"]

        product = Product.objects.get(id=productId)
        productVariant = ProductVariant.objects.get(id=productVariantId)
        productVariants = ProductVariant.objects.filter(variantProduct=product)
        firstProductVariant = ProductVariant.objects.filter(variantProduct=product).first()
        multipleImages = MultipleImages.objects.filter(multipleImageOfProduct=product)
        multipleImgList = []

        for image in multipleImages:
            multipleImgList.append(str(image.multipleImages.url))

        singleImage=str(productVariant.variantProduct.productImageFront)

        attributeObjects, attributeObjectsIds = get_product_attribute_list_for_quick_view(product.id)
        
        
        if product.productType == "Simple":
            productVariantMinPrice = None
            productVariantMaxPrice = None
            productVariantMinActualPrice = None
            productVariantMaxActualPrice = None
            productVariantActualPrice = product.product_actual_price_range
            productVariantDiscountRange = None
            productVariantDiscount = product.product_discount_range
            productVariantPrice1 = product.product_price_range

        if product.productType == "Classified":
            productVariantMinPrice = product.product_price_range[0]
            productVariantMaxPrice = product.product_price_range[1]
            productVariantMinActualPrice = product.product_actual_price_range[0]
            productVariantActualPrice = None
            productVariantMaxActualPrice = product.product_actual_price_range[1]
            productVariantDiscountRange = product.product_discount_range
            productVariantDiscount = None
            productVariantPrice1 = None
       
        
        data = {
            "productId": product.id,
            "firstProductVariant": firstProductVariant.id,
            "productVariantId": productVariant.id,
            "productName": productVariant.variantProduct.productName,
            "productFinalRating": product.productFinalRating,
            "productStockStatus": productVariant.productVariantStockStatus,
            "productVariantPrice1": productVariantPrice1,
            
            "productVariantMinPrice": productVariantMinPrice,
            "productVariantMaxPrice": productVariantMaxPrice,
        
            "productVariantMinActualPrice" : productVariantMinActualPrice,
            "productVariantMaxActualPrice" : productVariantMaxActualPrice,
            "productVariantDiscountRange" : productVariantDiscountRange,
            
            "productVariantActualPrice":productVariantActualPrice,
            "productVariantDiscount":productVariantDiscount,
            
            "productImageFront": str(product.productImageFront),
            "multipleImages": multipleImgList,
            "singleImage":singleImage,

            "productType": product.productType,
            
            "attributeObjects":attributeObjects,
            "attributeObjectsIds":attributeObjectsIds,

            "brand": str(product.productBrand),
            "category": str(product.proCategory)
        }

        return JsonResponse(data, safe=False)

def validate_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('couponCode')
        priceStr = data.get('price')
        taxstr = data.get('tax')
        finalAmountInUSDStr = data.get('priceInUSD')

        
        
        price = Decimal(priceStr)
        tax = Decimal(taxstr)
        finalAmountInUSD = Decimal(finalAmountInUSDStr)
        
        couponStatus = False
        
        coupon = Coupon.objects.filter(couponCode=coupon_code)
        couponObj=coupon.first()
        couponAmount = 0
        
        if len(coupon) == 1:
            couponStatus = True
            couponUsesByCustomer=CouponHistory.objects.filter(coupon=couponObj)
            if len(couponUsesByCustomer) < couponObj.usageLimit and int(couponObj.numOfCoupon) > 0:
                currentDateTime = timezone.now()
                if couponObj.expirationDateTime >= currentDateTime and price >= couponObj.minAmount:
                    if couponObj.couponType == "Fixed":
                        couponAmount=int(couponObj.couponDiscountOrFixed)
                    if couponObj.couponType == "Percentage":
                        couponDiscountAmount=((price*couponObj.couponDiscountOrFixed)/100)
                        couponAmount=couponDiscountAmount
        
        couponAmountForUSD = couponAmount
        currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        couponAmount=couponAmount*currency.factor
        finalAmount= (price-couponAmount)+(tax*currency.factor)
        finalAmountInUSD=finalAmountInUSD-couponAmountForUSD
        
        data = {'valid': couponStatus,'couponAmount':couponAmount,'currencySymbol':currency.symbol,
                'finalAmount':finalAmount,'finalAmountInUSD':finalAmountInUSD}
        return JsonResponse(data, safe=False)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@login_required(login_url='login_page')
def checkout_page(request):
    customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()

    customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    wishlist_products = customer_wishlist.wishlistProducts.all()
    totalWishlistProducts = wishlist_products.count()
    
    

    getTotalTax = customer_cart.getTotalTax
    getTotalPrice = customer_cart.getTotalPrice

    customer = CustomUser.objects.get(id=request.user.id)
    billingAddresses = OrderBillingAddress.objects.filter(customer=customer)
    
    
    cookie_value = request.COOKIES.get('couponCode')
    couponAmount = 0
    if cookie_value:
        coupon = Coupon.objects.filter(couponCode=cookie_value)
        couponObj=coupon.first()
        
        if len(coupon) == 1:
            couponUsesByCustomer=CouponHistory.objects.filter(coupon=couponObj)
            if len(couponUsesByCustomer) < couponObj.usageLimit and int(couponObj.numOfCoupon) > 0:
                currentDateTime = timezone.now()
                if couponObj.expirationDateTime >= currentDateTime and getTotalPrice >= couponObj.minAmount:
                    if couponObj.couponType == "Fixed":
                        couponAmount=int(couponObj.couponDiscountOrFixed)
                    if couponObj.couponType == "Percentage":
                        couponDiscountAmount=((getTotalPrice*couponObj.couponDiscountOrFixed)/100)
                        couponAmount=couponDiscountAmount
    else:
        pass
        
    currency = get_currency_instance(request)
    currency_code = currency.code
    getTotalPriceForRazorPay = (decimal.Decimal(float(getTotalPrice))) * currency.factor * 100
    couponAmountForRazorPay = (decimal.Decimal(float(couponAmount))) * currency.factor * 100
    getTotalTaxForRazorPay = (decimal.Decimal(float(getTotalTax))) * currency.factor * 100
    
    finalAmountForRazorPay=(getTotalPriceForRazorPay-couponAmountForRazorPay)+getTotalTaxForRazorPay
    payment = client.order.create({'amount': int(finalAmountForRazorPay), 'currency': currency_code, 'payment_capture': 1})
    finalAmount=(getTotalPrice-couponAmount)+getTotalTax
    
    context = {"breadcrumb": {"parent": "Checkout", "child": "Checkout"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "cart_products_demo": cart_products_demo,
               "getTotalTax": getTotalTax,
               "getFinalPriceAfterTax": finalAmount,
               
               "getTotalPrice": getTotalPrice,
               "couponAmount":couponAmount,
               "billingAddresses": billingAddresses,
               "payment": payment,
               "rsk": settings.RAZORPAY_KEY_ID,
               "ppl":settings.PAYPAL_CLIENT_ID
               }
        
    return render(request, 'pages/pages/checkout.html', context)

def payment_complete(request):
    body = json.loads(request.body)
    
    if 'addressId' in body:
        addressId = body["addressId"]
        strPrice = body["price"]
        
        decimalPrice=Decimal(strPrice)
        price=convert_amount_based_on_currency(decimalPrice,request)
        cartid = body["cartid"]
        orderpaymentmethodname = body["orderpaymentmethodname"]
        
        cookie_value = request.COOKIES.get('couponCode')
        if cookie_value:
            couponCode=cookie_value
        else:
            couponCode=''

        couponDiscountAmount=0  
        createHistory = False
        if couponCode:
            try:
                coupon=Coupon.objects.get(couponCode=couponCode)
                couponUsesByCustomer=CouponHistory.objects.filter(coupon=coupon)
                if len(couponUsesByCustomer) < coupon.usageLimit and int(coupon.numOfCoupon) > 0:
                    currentDateTime = timezone.now()
                    if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
                        if coupon.couponType == "Fixed":
                            price=price-int(coupon.couponDiscountOrFixed)
                        if coupon.couponType == "Percentage":
                            couponDiscountAmount=((price*coupon.couponDiscountOrFixed)/100)
                            price=price-couponDiscountAmount
                        createHistory = True
            except:
                pass

        order_billing_address_instance = OrderBillingAddress.objects.get(id=addressId)
        paymentmethod = PaymentMethod.objects.get(paymentMethodName=orderpaymentmethodname)

        if 'rpPaymentId' in body:
            rpPaymentId = body["rpPaymentId"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=rpPaymentId, orderAmount=price, orderPaymentMethodName=paymentmethod,)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()
            
            if createHistory:
                coupon.numOfCoupon=coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_copon= request.COOKIES.get('couponCode')
            if remove_copon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response 
            return JsonResponse(data={'message': 'Payment completed'},safe=False)

        if 'payPalTransactionID' in body:
            payPalTransactionID = body["payPalTransactionID"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=payPalTransactionID, orderAmount=price, orderPaymentMethodName=paymentmethod,)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()
            
            if createHistory:
                coupon.numOfCoupon=coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_copon= request.COOKIES.get('couponCode')
            if remove_copon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response 
            return JsonResponse(data={'message': 'Payment completed'},safe=False)
    else:
        strPrice = body["price"]
        decimalPrice=Decimal(strPrice)
        price=convert_amount_based_on_currency(decimalPrice,request)
        fname = body["fname"]
        lname = body["lname"]
        uname = body["uname"]
        email = body["email"]
        address1 = body["address1"]
        address2 = body["address2"]
        country = body["country"]
        city = body["city"]
        zip = body["zip"]
        cartid = body["cartid"]
        orderpaymentmethodname = body["orderpaymentmethodname"]
        
        cookie_value = request.COOKIES.get('couponCode')
        if cookie_value:
            couponCode=cookie_value
        else:
            couponCode=''
        
        couponDiscountAmount=0
        createHistory = False
        if couponCode:
            try:
                coupon=Coupon.objects.get(couponCode=couponCode)
                couponUsesByCustomer=CouponHistory.objects.filter(coupon=coupon)
                if len(couponUsesByCustomer) < coupon.usageLimit and int(coupon.numOfCoupon) > 0:
                    currentDateTime = timezone.now()
                    if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
                        if coupon.couponType == "Fixed":
                            price=price-int(coupon.couponDiscountOrFixed)
                        if coupon.couponType == "Percentage":
                            couponDiscountAmount=((price*coupon.couponDiscountOrFixed)/100)
                            price=price-couponDiscountAmount
                        createHistory = True
            except:
                pass     
            
        order_billing_address_instance = OrderBillingAddress.objects.create(customer=request.user, customerFirstName=fname, customerLastName=lname, customerUsername=uname,
                                                                            customerEmail=email, customerAddress1=address1, customerAddress2=address2, customerCountry=country, customerCity=city, customerZip=zip)
        order_billing_address_instance.save()
        paymentmethod = PaymentMethod.objects.get(paymentMethodName=orderpaymentmethodname)

        if 'rpPaymentId' in body:
            rpPaymentId = body["rpPaymentId"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=rpPaymentId, orderAmount=price, orderPaymentMethodName=paymentmethod)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()
            
            
            if createHistory:
                coupon.numOfCoupon=coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_copon= request.COOKIES.get('couponCode')
            if remove_copon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response 
            return JsonResponse(data={'message': 'Payment completed'},safe=False)

        if 'payPalTransactionID' in body:
            payPalTransactionID = body["payPalTransactionID"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user,
                                                                 orderPaymentTransactionId=payPalTransactionID,
                                                                 orderAmount=price, orderPaymentMethodName=paymentmethod)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()
            if createHistory:   
                coupon.numOfCoupon=coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_copon= request.COOKIES.get('couponCode')
            if remove_copon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response 
            return JsonResponse(data={'message': 'Payment completed'},safe=False)
  
        

def order_success(request): 
    if request.user.is_authenticated:
        customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()   
        
        customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
        wishlist_products = customer_wishlist.wishlistProducts.all()
        totalWishlistProducts = wishlist_products.count()
    
        customer = Customer.objects.get(customer=request.user)
    
        
        order = Order.objects.filter(orderedByCustomer=request.user.id).order_by('-orderCreatedAt').first()
    
        if order is not None:
            paymentmethod = order.orderPayment.orderPaymentMethodName
            products = ProductOrder.objects.filter(productOrderOrderId=order.id)
        else:
            paymentmethod = None
            products = []
    else:
        return redirect(request.META['HTTP_REFERER'])
    
    context = {
        "breadcrumb": {"parent": "Order-Success", "child": "child"},
        "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
        "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
        "orderid": order.id if order else None,
        "transactionId": order.orderPayment.orderPaymentTransactionId if order else None,
        "orderdate": order.orderCreatedAt if order else None,
        "orderprice": order.orderTotalPrice if order else None,
        "orderTax": order.orderTotalTax if order else None,
        "ordersubtotal": order.orderPrice if order else None,
        "products": products if order else None,
        "orderaddress": order.orderBillingAddress if order else None,
        "contactno": customer.customerContact,
        "paymentmethod": paymentmethod if order else None,
    }
    return render(request, 'pages/pages/order-success.html', context)


def order_tracking(request, id):
    customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    totalCartProducts = cart_products.count()

    customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    wishlist_products = customer_wishlist.wishlistProducts.all()
    totalWishlistProducts = wishlist_products.count()

    productOrders = OrderTracking.objects.filter(
        trackingOrderCustomer=request.user, trackingOrderOrderId=id)

    context = {"breadcrumb": {"parent": "Order Tracking", "child": "Order tracking"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "productOrders": productOrders
               }
    return render(request, 'pages/pages/order-tracking.html', context)

def user_dashboard(request):
    if request.user.is_authenticated:
        customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()

        customer_wishlist = Wishlist.objects.get(
            wishlistByCustomer=request.user.id)
        wishlist_products = customer_wishlist.wishlistProducts.all()
        totalWishlistProducts = wishlist_products.count()

        totalorder = ProductOrder.objects.filter(
            productOrderedByCustomer=request.user).count()
        pendingOrders = OrderTracking.objects.filter(trackingOrderCustomer=request.user).all().exclude(trackingOrderStatus="Delivered").count()

        products = ProductOrder.objects.filter(
            productOrderedByCustomer=request.user)
        orderaillingaddress = OrderBillingAddress.objects.filter(
            customer=request.user)
        lastAddress = OrderBillingAddress.objects.all().last()

        orders = Order.objects.filter(orderedByCustomer=request.user)
    else:
        return redirect('login_page')

    context = {"breadcrumb": {"parent": "User Dashboard", "child": "User Dashboard"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "totalorder": totalorder, "pendingOrders": pendingOrders,
               "orderaillingaddress": orderaillingaddress, "products": products,
               "orders": orders, "lastAddress": lastAddress,
               "userId": request.user.id
               }
    return render(request, 'pages/pages/user-dashboard.html', context)

def contact_us(request):
    if request.method == 'POST':
        firstname = request.POST['first']
        lastname = request.POST['last']
        email = request.POST['email']
        confirm_email = request.POST['email2']
        number = request.POST['number']
        comment = request.POST['comment']
        name=str(firstname)+" "+str(lastname)

        if ContactUs.objects.filter(contactUsEmail=email).exists():
            messages.warning(request, 'Email already exists')
        else:
            if email == confirm_email:
                user = ContactUs.objects.create(contactUsName=name, contactUsEmail=email,contactUsNumber=number ,contactUsComment=comment)
                user.save()
                messages.success(request, 'Your form has been submitted successfully')
                return redirect('contact_us')
            else:
                messages.error(request, 'Email Does Not Match')
                return redirect('contact_us')
        return render(request, 'pages/pages/contact-us.html')
    else:
        context = {"breadcrumb": {"parent": "Contact Us", "child": "Contact Us"},
                }
        return render(request, 'pages/pages/contact-us.html', context)

def search_bar(request, params=None):
    query = ''
    data = ''
    products = ProductVariant.objects.all()
    if 'search' in request.GET:
        query = request.GET.get('search')

        if query:
            if params:
                products = ProductVariant.objects.filter(
                    variantProduct__productName__icontains=query)
                data = [{'id': p.variantProduct.id, 'name': p.variantProduct.productName, 'category': p.variantProduct.proCategory.categoryName,
                         'brand': p.variantProduct.productBrand.brandName, 'description': p.variantProduct.productDescription, } for p in products]
            else:
                products = ProductVariant.objects.all()

    products = GetUniqueProducts(products)
    paginator = Paginator(products,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {"breadcrumb": {"parent": "Search", "child": "Search"}, 'products': products,
               'query': query,'page_obj':page_obj,
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
    
    return render(request, 'pages/pages/search.html', context)

def page_not_found(request):
    cart_products,totalCartProducts = show_cart_popup(request)
    context = {"breadcrumb": {"parent": 404, "child": 404},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
    return render(request, 'pages/pages/404.html', context)

def coming_soon(request):
    context = {"breadcrumb": {"parent": "Coming Soon", "child": "Coming Soon"}}
    return render(request, 'pages/pages/coming-soon.html', context)

def review(request):
    context = {"breadcrumb": {"parent": "Review", "child": "Review"}}
    return render(request, 'pages/pages/review.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['emailname']
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            otp = generateOTP()
            message = render_to_string('authentication/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': otp,
            })
            to_email = email
            mail = EmailMultiAlternatives(mail_subject, message, to=[to_email])
            mail.attach_alternative(message, "text/html")
            mail.send()
            temDataObject = TemporaryData.objects.get(
                TemporaryDataByUser__email=email)
            temDataObject.otpNumber = otp

            current_time = datetime.now()
            temDataObject.otpExpiryTime = current_time + timedelta(minutes=1)
            temDataObject.save(update_fields=['otpNumber', 'otpExpiryTime'])

            response = HttpResponseRedirect('verify_token')
            response.set_cookie('code', user.id, max_age=180)
            messages.success(
                request, 'An OTP has been sent to your email address successfully')
            return response
        else:
            messages.error(request, 'Account Does Not Exist!')
            return redirect('forgot_password')
    return render(request, 'authentication/forgot.html')

def verify_token(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        get_id = request.COOKIES['code']
        get_user = CustomUser.objects.get(id=get_id)

        temDataObject=TemporaryData.objects.get(TemporaryDataByUser=get_user)
        temDataObject = TemporaryData.objects.get(TemporaryDataByUser=get_user)
        stored_otp = temDataObject.otpNumber
        current_time = timezone.now()
        exp_time = temDataObject.otpExpiryTime

        if current_time < exp_time:
            if entered_otp == stored_otp:
                messages.success(request, 'OTP Verified')
                return redirect('update_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('verify_token')
        else:
            messages.error(
                request, 'Your otp has been expired! Please regenerate otp.')
            return redirect('forgot_password')
    return render(request, 'authentication/verify_token.html')

def update_password(request):
    if request.method == 'POST':
        password = request.POST['newpass']
        conf_password = request.POST['confnewpass']

        password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        user = CustomUser.objects.get(username__exact=request.user.username)
        if password and conf_password:
            if not re.search(password_pattern, password):
                messages.warning(
                    request, 'Password must be at least 8 characters long and contain at least one letter and one number')
                return redirect('update_password')

            if password == conf_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('login_page')
            else:
                messages.error(request, 'Password Does Not Match')
                return redirect('update_password')
    return render(request, 'authentication/update_password.html')

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['currentpass']
        new_password = request.POST['newpass']
        confirm_password = request.POST['confnewpass']

        user = CustomUser.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
                return redirect('login_page')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password Does Not Match')
            return redirect('change_password')
    else:
        return render(request, 'authentication/change_password.html')


def remove_address(request, id):
    address = OrderBillingAddress.objects.get(id=id, customer=request.user)
   
    product_orders = ProductOrder.objects.filter(productOrderedByCustomer__username=address)
   
    
    associated_orders = Order.objects.filter(orderBillingAddress=address)
    if associated_orders:
        for order in associated_orders:
            if order.orderedOrNot == True:
                address.delete()
                messages.success(request,'Address Removed Successfully')
                return redirect('user_dashboard')
            else:    
                messages.warning(request,'Address cannot be removed as it is associated with a delivered order')
                return redirect('user_dashboard')
        else:
            address.delete()
            messages.success(request,'Address Removed Successfully')
            return redirect('user_dashboard')
    else:
        address.delete()
        messages.success(request,'Address Removed Successfully')
        return redirect('user_dashboard')
    


def get_address(request):
     if request.method == 'POST':
        body = json.loads(request.body)
        addressId = body['addressId']
        address=OrderBillingAddress.objects.get(id=addressId)
        data = {'fname': address.customerFirstName, 'lname': address.customerLastName, 'username': address.customerUsername, 'email': address.customerEmail, 'mobno': address.customerMobile,
        'address1': address.customerAddress1, 'address2': address.customerAddress2, 'country': address.customerCountry, 'city': address.customerCity, 'zipcode': address.customerZip}
        return JsonResponse(data, safe=False)


def add_address(request):
    body = json.loads(request.body)
    fname = body["fname"]
    lname = body["lname"]
    username = body["username"]
    email = body["email"]
    mobno = body["mobno"]
    address1 = body["address1"]
    address2 = body["address2"]
    country = body["country"]
    city = body["city"]
    zipcode = body["zipcode"]
    customer = CustomUser.objects.get(id=request.user.id)
    user = OrderBillingAddress.objects.create(customer=customer,customerFirstName=fname,customerLastName=lname,customerUsername=username,customerEmail=email,customerMobile=mobno,customerAddress1=address1,customerAddress2=address2,customerCountry=country,customerCity=city,customerZip=zipcode)
    user.save()
    return HttpResponse(request, status=200)


def save_address(request):
    if request.method == "POST":
        body = json.loads(request.body)
        addressId = body['addressId']
        addressGet=OrderBillingAddress.objects.get(id=addressId)
        addressGet.customerFirstName = body['fNameEle']
        addressGet.customerLastName = body['lNameEle']
        addressGet.customerUsername = body['userNameEle']
        addressGet.customerEmail = body['emailEle']
        addressGet.customerMobile = body['mobileEle'] 
        addressGet.customerAddress1 = body['addOneEle'] 
        addressGet.customerAddress2 = body['addTwoEle'] 
        addressGet.customerCountry = body['countryEle'] 
        addressGet.customerCity = body['cityEle'] 
        addressGet.customerZip = body['zipEle'] 
        addressGet.save()
        return HttpResponse(status=200)
 
        
def delete_user(request):
    user = request.user
    user.delete()
    return HttpResponse({'success': True})

# Blog Pages Section

def blog_details(request, id):
    blog = Blog.objects.get(id=id)
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    blogCategories = BlogCategory.objects.all()
    blogComments = BlogComment.objects.filter(
        commentOfBlog__id=id, status=True)
    relatedBlogs = Blog.objects.filter(
        blogCategory=blog.blogCategory, status=True, blogStatus=1).exclude(id=id)
    
    cart_products,totalCartProducts = show_cart_popup(request)

            
    context = {"breadcrumb": {"parent": "Blog Details", "child": "Blog Details"},
            "blog": blog,
            "blogs": blogs,
            "blogCategories": blogCategories,
            "blogComments": blogComments,
            "relatedBlogs": relatedBlogs,
            "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
        
    return render(request, 'pages/blog/blog-details.html', context)


def add_comment(request, id):
    if request.method == 'POST':
        comment = request.POST['comment']
        blog = Blog.objects.get(id=id)
        commentInstance = BlogComment.objects.create(
            commentOfBlog=blog, commentByUser=request.user, comment=comment)
        commentInstance.save()
        return redirect('blog_details', id=id)


def infinite_scroll(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)
    blogCategories = BlogCategory.objects.all()
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)

    
    context = {"breadcrumb": {"parent": "Blog Infinite Scroll",
                              "child": "Blog Infinite Scroll"},
               "blogs": blogs,
               "blogCategories": blogCategories,
               "page_obj": page_obj,
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
    return render(request, 'pages/blog/blog-infinite-scroll.html', context)


def left_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)
    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Blog Left Sidebar", "child": "Blog Left Sidebar"},
               "blogs": blogs,
               "blogCategories": blogCategories,
               "page_obj": page_obj,
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,}

    return render(request, 'pages/blog/blog-left-sidebar.html', context)


def left_sidebar_for_selected_category(request, id):
    blogCategory = BlogCategory.objects.get(id=id)
    blogs = Blog.objects.filter(
        status=True, blogStatus=1, blogCategory=blogCategory)

    paginator = Paginator(blogs, 3)
    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Blog Left Sidebar", "child": "Blog Left Sidebar"},
               "blogs": blogs,
               "blogCategories": blogCategories,
               "page_obj": page_obj,
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
    return render(request, 'pages/blog/blog-left-sidebar.html', context)


def listing(request):
    blogs=Blog.objects.filter(status=True,blogStatus=1)
    paginator = Paginator(blogs, 5)                    
    paginator = Paginator(blogs,3)                     
    blogCategories=BlogCategory.objects.all()
   
   
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {
        "breadcrumb": {"parent": "Blog Listing", "child": "Blog Listing"},
        "blogs": blogs,
        "blogCategories": blogCategories,
        "page_obj": page_obj,
        "cart_products": cart_products, "totalCartProducts": totalCartProducts,
    }
    return render(request, "pages/blog/blog-listing.html", context)


def masonary(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)
    blogCategories = BlogCategory.objects.all()
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {
        "breadcrumb": {"parent": "Blog Masonary", "child": "Blog Masonary"},
        "blogs": blogs,
        "blogCategories": blogCategories,
        'page_obj':page_obj,
        "cart_products": cart_products, "totalCartProducts": totalCartProducts,
    }
    return render(request, "pages/blog/blog-masonary.html", context)


def no_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {
        "breadcrumb": {"parent": "Blog No Sidebar", "child": "Blog No Sidebar"},
        "blogs": blogs,
        "page_obj": page_obj,
        "cart_products": cart_products,"totalCartProducts": totalCartProducts,
        }
    return render(request, "pages/blog/blog-no-sidebar.html", context)


def right_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)

    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {
        "breadcrumb": {"parent": "Blog Right Sidebar", "child": "Blog Right Sidebar"},
        "blogs": blogs,
        "blogCategories": blogCategories,
        "page_obj": page_obj,
        "cart_products": cart_products,"totalCartProducts": totalCartProducts,

    }
    return render(request, "pages/blog/blog-right-sidebar.html", context)


def customer_review(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        productId = body["productId"]
        reviewText = body["reviewText"]
        ratingValue = body["ratingValue"]
        product = Product.objects.get(id=productId)
        ProductReview.objects.create(productName=product, productReviewByCustomer=request.user,
                                     productReview=reviewText, productRatings=ratingValue)
        return HttpResponse(status=200)
    
    
def show_cart_popup(request):
    if request.user.is_authenticated:
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()
    else:
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart' or None) is not None else None
        totalCartProducts = 0
        if (get_Item is not None and get_Item != "null"):
            cart_products = json.loads(get_Item)
            totalCartProducts = len(cart_products)
        else:
            cart_products = []
            totalCartProducts = 0
    return cart_products,totalCartProducts


def user_authenticate(request):
    is_authenticated = request.user.is_authenticated
    data = {'is_authenticated': is_authenticated}
    return JsonResponse(data)






def cart_page(request,cart_products=None):
    current_user = request.user
    customer_cart = request.user
    totalCartProducts = 0
    cartTotalPriceAfterTax = 0
    cart_products = []
    
    context = {"breadcrumb": {"parent": "Shopping Cart", "child": "Cart"},
               }

    if current_user.is_authenticated:
        try:
            customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        except Cart.DoesNotExist:
            customer_cart = Cart.objects.create(cartByCustomer=request.user)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()
        cartTotalPriceAfterTax = customer_cart.getFinalPriceAfterTax
        context["cartId"]=customer_cart.id,
    else:
        try:  
            customer_cart = Cart.objects.create(cart_id=_cart_id(request))
        except Cart.DoesNotExist:   
            customer_cart = Cart.objects.create(cart_id=_cart_id(request))
            
        get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None
        if get_Item:
            cart_products = json.loads(get_Item)  # Default to an empty list if no data
            
            for item in cart_products:
                item['totalPrice'] = int(item['quantity']) * float(item['price'])

        totalCartProducts = len(cart_products)
        TotalTax,TotalTaxPrice,cartTotalPriceAfterTax = get_total_tax_values(cart_products)
        TotalPrice = sum([float(i['totalPrice']) for i in cart_products])
        context["cartTotalPrice"]=TotalPrice
        context["cartTotalTax"]=TotalTaxPrice
        cartTotalPriceAfterTax = TotalPrice + TotalTaxPrice
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    context["cart_products"]= cart_products
    context["totalCartProducts"]= totalCartProducts
    context["cartTotalPriceAfterTax"]= cartTotalPriceAfterTax
    context["Cart"]= customer_cart
    context["cartId"]=customer_cart.id
    context['active_banner_themes']=active_banner_themes

    return render(request, 'pages/pages/cart.html', context)