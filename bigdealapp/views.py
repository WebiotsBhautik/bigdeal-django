from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.conf import settings
from collections import Counter
from django.urls import reverse
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from accounts.models import CustomUser,TemporaryData, Customer
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import auth
from .models import Banner,BannerTheme, BannerType, BlogCategory, Blog, BlogComment,ContactUs,Coupon,CouponHistory
from product.models import (AttributeName, MultipleImages, ProBrand, ProCategory, Product,
                            ProductAttributes, ProductReview, ProductVariant,AttributeValue,ProductMeta)

from order.models import (Cart,CartProducts,OrderBillingAddress,OrderPayment,Order,OrderTracking,ProductOrder,Wishlist,Compare,PaymentMethod)

from bigdealapp.helpers import get_color_and_size_list, get_currency_instance, GetUniqueProducts, IsVariantPresent, GetRoute, create_query_params_url, generateOTP, get_product_attribute_list, get_product_attribute_list_for_quick_view, search_query_params_url, convert_amount_based_on_currency


from currency.models import Currency
from decimal import Decimal, ROUND_HALF_UP
from django.http import Http404
import json
import decimal
import razorpay

from decimal import Decimal, ROUND_HALF_UP


# Imports For Forgot Password With Email Verification

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
# from django.contrib.auth.tokens import default_token_generator,PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
from django.utils import timezone
import re
from django.db.models import Q,Sum
from django.views.decorators.csrf import csrf_exempt, csrf_protect






# Create your views here.


def setCookie(request):
    response = HttpResponse('Cookie Set')
    response.set_cookie('login_status', True)
    currency = Currency.objects.get(code='USD')
    response.set_cookie('currency', currency.id)
    return response

def set_currency_to_session(request):
    body = json.loads(request.body)
    currencyID = body['currencyId']
    response = HttpResponse('Cookie Set for currency')
    response.set_cookie('currency', currencyID)
    return response


def get_selected_currency(request):
    currency_cookie = request.COOKIES.get('currency')
    if currency_cookie:
        try:
            currency = Currency.objects.get(id=currency_cookie)
        except Currency.DoesNotExist:
            raise Http404("Currency does not exist")
    else:
        currency = None

    if currency is None:
        currency = Currency.objects.get(code='USD')
        
    data = {"factor": currency.factor, "symbol": currency.symbol}
    return JsonResponse(data, safe=False)


def add_cookie_currency(request):
    currency_cookie = request.COOKIES.get('currency')
    if currency_cookie:
        try:
            selected_currency = Currency.objects.get(id=currency_cookie)
        except Currency.DoesNotExist:
            raise Http404("Currency does not exist")
    else:
        selected_currency = None

    if selected_currency is None:
        selected_currency = Currency.objects.get(code='USD')

    return selected_currency


def signup_page(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    if request.method == "POST":
        role = request.POST['role']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['pass']
        confpassword = request.POST['cpass']

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email address is already in use')
        else:
            if password == confpassword:
                if role == 'customer':
                    user = CustomUser.objects.create_user(username=username, email=email, is_customer=True, is_vendor=False, password=password)
                    group = Group.objects.get(name='Customer')
                    user.groups.add(group)
                    user.save()
                    messages.success(request, 'Registration successfully')
                    return redirect('login_page')
                else:
                    user = CustomUser.objects.create_user(
                        username=username, email=email, is_customer=False, is_vendor=True, password=password)
                    group = Group.objects.get(name='Vendor')
                    user.groups.add(group)
                    user.save()
                    messages.success(request, 'Registration successfully')
                    return redirect('login_page')
            else:
                messages.error(request,'Password Does Not Match')
                return redirect('signup_page')
        return render(request, 'authentication/sign-up.html')
    else:
        context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
                   'active_banner_themes':active_banner_themes,}
        return render(request, 'authentication/sign-up.html', context)
                    

def login_page(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    if request.method == "POST":
        username = request.POST['name']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None and user.is_customer:
            auth.login(request,user)
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
        
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
    
    context = {"breadcrumb": {
         "parent": "Dashboard", "child": "Default"},
               'active_banner_themes':active_banner_themes,
               **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'authentication/login.html',context)

def logout_page(request):
    auth.logout(request)
    return redirect('/login_page')


# HOME PAGES SECTION 

def delete_old_currencies(request,response):
    if not request.session.get('cookies_deleted', False):
        for cookie in request.COOKIES:
            response.delete_cookie(cookie)
            request.session['cookies_deleted'] = True
    return response
    

def handle_cart_logic(request):
    context = {}
    cart_products = {}
    if request.user.is_authenticated:
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

    return context

def index(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore1 Demo')
    collection_banner  = banners.filter(bannerType__bannerTypeName='Collection Banner')
    col_banner = {}
    if collection_banner.count() >= 1:
        col_banner = [collection_banner[0],]

    brands = ProBrand.objects.all()
    layout1_category = ProCategory.objects.get(categoryName='ms1')
    subcategories = layout1_category.get_descendants(include_self=True)
    layout1_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
     # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
                
    cart_products,totalCartProducts = show_cart_popup(request)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbrands':brands,
               'allbanners':banners,
               'layout1_products':layout1_products,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'col_banner':col_banner,
               'cart_products':cart_products,
               'theme':'ms1',
               "totalCartProducts": totalCartProducts,
               'active_banner_themes':active_banner_themes,
                **cart_context,
               }
        
    template_path = 'pages/home/ms1/index.html'
   
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    
    # Deleting all old cookies
    if not request.session.get('cookies_deleted', False):
        for cookie in request.COOKIES:
            response.delete_cookie(cookie)  
        request.session['cookies_deleted'] = True

        
    # Setting the new cookie
    response.set_cookie('currency', currency.id)
    return response


def layout2(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore2 Demo')
    shop_banners = banners.filter(bannerType__bannerTypeName='Banner')
    media_banners = banners.filter(bannerType__bannerTypeName='Media Banner')

    if shop_banners.count() == 2:
        both_banners = [shop_banners[0], shop_banners[1]]

    brands = ProBrand.objects.all()
    layout2_category = ProCategory.objects.get(categoryName='ms2')
    subcategories = layout2_category.get_descendants(include_self=True)
    layout2_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
     # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    blogs = Blog.objects.filter(blogCategory__categoryName='layout2',status=True, blogStatus=1)

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
                'both_banners':both_banners,
               'layout2_products':layout2_products,
               'media_banners':media_banners,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'blogs':blogs,
                'theme':'ms2',
               'active_banner_themes':active_banner_themes,
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
                **cart_context,
               }
    
    return render(request, 'pages/home/ms2/layout-2.html',context)

def layout3(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore3 Demo')
    media_banners = banners.filter(bannerType__bannerTypeName='Media Banner')
    left_banners = banners.filter(bannerType__bannerTypeName='Left Banner')

    brands = ProBrand.objects.all()
    layout3_category = ProCategory.objects.get(categoryName='ms3')
    subcategories = layout3_category.get_descendants(include_self=True)
    layout3_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products  
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

        
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
               'layout3_products':layout3_products,
               'media_banners':media_banners,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'left_banners':left_banners,
               'theme':'ms3',
               'active_banner_themes':active_banner_themes,
               **cart_context,
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
               }
        
    return render(request, 'pages/home/ms3/layout-3.html',context)

def layout4(request):   
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Megastore4 Demo')
    media_banners = banners.filter(bannerType__bannerTypeName='Media Banner')

    
    brands = ProBrand.objects.all()
    layout4_category = ProCategory.objects.get(categoryName='ms4')
    subcategories = layout4_category.get_descendants(include_self=True)
    layout4_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
     # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products  
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)


    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
               'media_banners':media_banners,
               'layout4_products':layout4_products,
               'subcategories':subcategories,
               'theme':'ms4',
               'products_by_subcategory':products_by_subcategory,
                'active_banner_themes':active_banner_themes,
                **cart_context,
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,

               }
    
    return render(request, 'pages/home/ms4/layout-4.html',context)

def layout5(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Megastore5 Demo')
    collection_banner  = banners.filter(bannerType__bannerTypeName='Collection Banner')
    sale_banner  = banners.filter(bannerType__bannerTypeName='Sale Banner')

    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    
    if collection_banner.count() == 4:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
    
    brands = ProBrand.objects.all()
    layout5_category = ProCategory.objects.get(categoryName='ms5')
    subcategories = layout5_category.get_descendants(include_self=True)
    layout5_products = Product.objects.filter(proCategory__in=subcategories)

    main_categories = ProCategory.objects.filter(parent=layout5_category)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products  
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'allbrands':brands,
            'layout5_category':layout5_category,
            'layout5_products':layout5_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'collection_banner':collection_banner,
            'sale_banner':sale_banner,
            'theme':'ms5',
            'main_categories':main_categories,
            'active_banner_themes':active_banner_themes,
             **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

            }
    
    
    
    return render(request, 'pages/home/ms5/layout-5.html',context)

def electronics(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Electronics Demo')
    media_banners = banners.filter(bannerType__bannerTypeName='Media Banner')

    brands = ProBrand.objects.all()
    
    electronics_category = ProCategory.objects.get(categoryName='Electronics')
    subcategories = electronics_category.get_descendants(include_self=True)
    electronics_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products  
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Electronics',status=True, blogStatus=1)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'allbrands':brands,
            'electronics_category':electronics_category,
            'electronics_products':electronics_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'media_banners':media_banners,
            'blogs':blogs,
            'theme':'Electronics',
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,
            }
    return render(request, 'pages/home/electronics/electronics.html',context)

def vegetable(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Vegetable Demo')
    masonary_banner = banners.filter(bannerType__bannerTypeName='masonary-banner')
    
    first_banner = {}
    second_banner = {}
    third_banner = {}
    four_banner = {}
    five_banner = {}
    six_banner = {}
    
    if masonary_banner.count() == 6:
        first_banner = masonary_banner[0]
        second_banner = masonary_banner[1]
        third_banner = masonary_banner[2]
        four_banner = masonary_banner[3]
        five_banner = masonary_banner[4]
        six_banner = masonary_banner[5]
        
    
    vegetable_category = ProCategory.objects.get(categoryName='Vegetables')
    subcategories = vegetable_category.get_descendants(include_self=True)
    # subcategories = ProCategory.objects.get(categoryName='Vegetables').get_descendants(include_self=True)

    vegetable_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products  
        
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Vegetables',status=True, blogStatus=1)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'vegetable_category':vegetable_category,
            'vegetable_products':vegetable_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Vegetables',
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'four_banner':four_banner,
            'five_banner':five_banner,
            'six_banner':six_banner,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,
            }

    return render(request, 'pages/home/vegetables/vegetable.html',context)

def furniture(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Furniture Demo')
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    five_banner = {}
    
    if collection_banner.count() == 5:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
        five_banner = collection_banner[4]
        
    
    furniture_category = ProCategory.objects.get(categoryName='Furniture')
    subcategories = furniture_category.get_descendants(include_self=True)
    
    furniture_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Furniture',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
        
    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'furniture_category':furniture_category,
            'furniture_products':furniture_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Furniture',
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,
            }
    return render(request, 'pages/home/furniture/furniture.html',context)

def cosmetic(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Cosmetic Demo')
    
    main_banner = list(banners.filter(bannerType__bannerTypeName='Banner'))
    last_two_banners = main_banner[-2:]
    
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    
    if collection_banner.count() == 4:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
    
    cosmetic_category = ProCategory.objects.get(categoryName='Cosmetic')
    subcategories = cosmetic_category.get_descendants(include_self=False)
    
    cosmetic_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products

    blogs = Blog.objects.filter(blogCategory__categoryName='Cosmetic',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

        
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'last_two_banners':last_two_banners,
            'cosmetic_category':cosmetic_category,
            'cosmetic_products':cosmetic_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Cosmetic',
           'first_banner':first_banner,
           'second_banner':second_banner,
           'third_banner':third_banner,
           'fourth_banner':fourth_banner,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,
            }
    
    return render(request,'pages/home/cosmetic/cosmetic.html',context)

def kids(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Kids Demo')
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    five_banner = {}
    
    if collection_banner.count() == 5:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
        five_banner = collection_banner[4]
        
        
    kids_category = ProCategory.objects.get(categoryName='Kids')
    subcategories = kids_category.get_descendants(include_self=False)
    
    kids_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products

    blogs = Blog.objects.filter(blogCategory__categoryName='Kids',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

        

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
        #     'last_two_banners':last_two_banners,
            'kids_category':kids_category,
            'kids_products':kids_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Kids',
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,
        }   

    return render(request, 'pages/home/kids/kids.html',context)

def tools(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Tools Demo')
    collection_banner = list(banners.filter(bannerType__bannerTypeName='Collection Banner'))
    last_three_collection = collection_banner[-3:]

    tools_category = ProCategory.objects.get(categoryName ='Tools')
    subcategories = tools_category.get_descendants(include_self=False)
    
    tools_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Tools',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

                                            
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'tools_category':tools_category,
            'tools_products':tools_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'last_three_collection':last_three_collection,
            'blogs':blogs,
            'theme':'Tools',
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

            }   
    return render(request, 'pages/home/tools/tools.html',context)

def grocery(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Grocery Demo')
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    testimonial_banner= list(banners.filter(bannerType__bannerTypeName='testimonial Banner'))
    last_testimonial = testimonial_banner[-1:]
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    five_banner = {}
    six_banner = {}
    
    if collection_banner.count() >= 5:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
        five_banner = collection_banner[4]
        
        
    masonary_banner = banners.filter(bannerType__bannerTypeName='masonary-banner')
    if masonary_banner.count() >= 6:
        first_banner = masonary_banner[0]
        second_banner = masonary_banner[1]
        third_banner = masonary_banner[2]
        fourth_banner = masonary_banner[3]
        five_banner   = masonary_banner[4]
        six_banner = masonary_banner[5]
    
    
    grocery_category = ProCategory.objects.get(categoryName ='Grocery')
    subcategories = grocery_category.get_descendants(include_self=False)
    
    grocery_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Grocery',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'grocery_category':grocery_category,
            'grocery_products':grocery_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Grocery',
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
            'six_banner':six_banner,
            'last_testimonial':last_testimonial,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

            }   
    return render(request, 'pages/home/grocery/grocery.html',context)

def pets(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Pets Demo')
    mainslider = banners.filter(bannerType__bannerTypeName='Sideslider')
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    
    if collection_banner.count() >= 4:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
        
    pets_category = ProCategory.objects.get(categoryName ='Pets')
    subcategories = pets_category.get_descendants(include_self=False)
    
    pets_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Pets',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)


    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'mainslider':mainslider,
            'pets_category':pets_category,
            'pets_products':pets_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'theme':'Pets',
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            # 'five_banner':five_banner,
            # 'six_banner':six_banner,
            # 'last_testimonial':last_testimonial,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

            }   
    
    return render(request, 'pages/home/pets/pets.html',context)

def farming(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Farming Demo')
    collection_banner = banners.filter(bannerType__bannerTypeName='Collection Banner')
    	
    last_sale_banner  = list(banners.filter(bannerType__bannerTypeName='Sale Banner'))
    sale_banner = last_sale_banner[-1:]
    
    last_counter_banner  = list(banners.filter(bannerType__bannerTypeName='Counter Banner'))
    counter_banner = last_counter_banner[-1:]
    

    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    
    if collection_banner.count() == 4:
        first_banner = collection_banner[0]
        second_banner = collection_banner[1]
        third_banner = collection_banner[2]
        fourth_banner = collection_banner[3]
        
        
    farming_category = ProCategory.objects.get(categoryName='Farming')
    subcategories = farming_category.get_descendants(include_self=True)
    
    farming_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Farming',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

        

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'farming_category':farming_category,
            'farming_products':farming_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'blogs':blogs,
            'theme':'Farming',
            'sale_banner':sale_banner,
            'counter_banner':counter_banner,
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

        }
    return render(request, 'pages/home/farming/farming.html',context)

def digital_marketplace(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName = 'Digital Marketplace demo')
    mainslider = banners.filter(bannerType__bannerTypeName='Sideslider')
    pricingBanners = banners.filter(bannerType__bannerTypeName='Pricing Banner')
    first_banner = {}
    second_banner = {}
    third_banner = {}
    fourth_banner = {}
    
    if pricingBanners.count() >= 4:
        first_banner = pricingBanners[0]
        second_banner = pricingBanners[1]
        third_banner = pricingBanners[2]
        fourth_banner = pricingBanners[3]
        
    
    digital_category = ProCategory.objects.get(categoryName='Digital-Marketplace')
    subcategories = digital_category.get_descendants(include_self=False)
    
    digital_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory={}
    
    # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products
        
        
    blogs = Blog.objects.filter(blogCategory__categoryName='Digital Marketplace',status=True, blogStatus=1)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'mainslider':mainslider,
            'digital_category':digital_category,
            'digital_products':digital_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'blogs':blogs,
            'theme':'Digital Marketplace',
            'active_banner_themes':active_banner_themes,
            **cart_context,
            'cart_products':cart_products,
            'totalCartProducts':totalCartProducts,

        }
    return render(request, 'pages/home/digital_marketplace/digital-marketplace.html',context)


# SHOP PAGES SECTION 

def filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary):
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = add_cookie_currency(request)
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        brands = selected_allbrand.split(',')[:-1]
        product = []
        for brand in brands:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brand)
            product += product1

    if attributeDictionary:
        for attribute in attributeDictionary:
            if attributeDictionary[attribute]:
                if type(product) is not list:
                    attribute_filter = product
                else:
                    productIdList = [p.id for p in product]
                    attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
                values = attributeDictionary[attribute].split(',')[:-1]
                product = []
                for value in values:
                    attributeNameObj = AttributeName.objects.get(attributeName=attribute)
                    product1 = attribute_filter.filter(
                        productVariantAttribute__attributeName=attributeNameObj,
                        productVariantAttribute__attributeValue=value
                    )
                    product += product1

    return product

def shop_left_sidebar(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()
    
    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)
    
    
    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = 0
    max_price = 0
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    template_path = 'pages/shop/shop-left-sidebar.html'
        
    context = {"breadcrumb": {"parent": "Shop Left Sidebar", "child": "Shop Left Sidebar"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_left_sidebar',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            'totalCartProducts': totalCartProducts,
            **cart_context,

            }
    
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_right_sidebar(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = 0
    max_price = 0
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-right-sidebar.html'
    
    context = {"breadcrumb": {"parent": "Shop Right Sidebar", "child": "Shop Right Sidebar"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_right_sidebar',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_no_sidebar(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = 0
    max_price = 0
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-no-sidebar.html'
    
    context = {"breadcrumb": {"parent": "Shop No Sidebar", "child": "Shop No Sidebar"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_no_sidebar',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,

            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_sidebar_popup(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()
    
    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = 0
    max_price = 0
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-sidebar-popup.html'
    
    context = {"breadcrumb": {"parent": "Shop Sidebar Popup", "child": "Shop Sidebar Popup"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_sidebar_popup',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_metro(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore1 Demo')
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = 0
    max_price = 0
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-metro.html'
    
    context = {"breadcrumb": {"parent": "Shop Metro", "child": "Shop Metro"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'allbanners': banners,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_metro',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_full_width(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore1 Demo')
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-full-width.html'

    context = {"breadcrumb": {"parent": "Shop Full Width", "child": "Shop Full Width"},
            'allbanners': banners,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_infinite_scroll(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)
    
    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    # paginator = Paginator(product,5)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-infinite-scroll.html'
    
    context = {"breadcrumb": {"parent": "Shop Infinite Scroll", "child": "Shop Infinite Scroll"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            # 'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_infinite_scroll',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context, 
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_3grid(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)
    
    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
      
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-3-grid.html'
    
    context = {"breadcrumb": {"parent": "Shop 3grid", "child": "Shop 3grid"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_3grid',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_6grid(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)   
    
    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-6-grid.html'
    
    context = {"breadcrumb": {"parent": "Shop 6grid", "child": "Shop 6grid"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_6grid',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }
    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response

def shop_list_view(request):
    url = ''
    selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
    selected_allprice = request.GET['price'] if 'price' in request.GET else []

    attributeNameList = []
    attributeDictionary = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeNameList.append(attribute.attributeName)
        
    for attribute in attributeNameList:
        attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []
        
    brand = ProBrand.objects.all()
    category = ProCategory.objects.all()
    product = ProductVariant.objects.all()
    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()
     
    product = filter_products(request, product, selected_allbrand, selected_allprice, attributeDictionary)

    attributeDict = {}
    attributeName = AttributeName.objects.all()
    for attribute in attributeName:
        attributeDict[attribute.attributeName]=[]
        attributeValue = AttributeValue.objects.filter(attributeName=attribute)
        for value in attributeValue:
            attributeDict[attribute.attributeName].append(value.attributeValue)
            
    product = GetUniqueProducts(product)
    totalProduct = len(product)
    paginator = Paginator(product,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
    min_price = []
    max_price = []
    selected_currency = []
    
    if get_all_prices:
        min_price = min(list(get_all_prices))
        max_price = max(list(get_all_prices))
        
    
    selected_currency = add_cookie_currency(request)
    if selected_currency:
        min_price = min_price*selected_currency.factor
        max_price = max_price*selected_currency.factor
        
        
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    template_path = 'pages/shop/shop-list-view.html'
    
    context = {"breadcrumb": {"parent": "Shop List View", "child": "Shop List View"},
            'shop_banner':shop_banner,'sidebar_banner':sidebar_banner,
            'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
            'productVariant':product,
            'url':url,
            'select_brands':selected_allbrand,
            'page_obj':page_obj,
            'attributeDict':attributeDict,
            'min_price':min_price,
            'max_price':max_price,
            'symbol':selected_currency.symbol,
            'last_added_products':last_added_products,
            'path':'shop_list_view',
            'totalCount':totalProduct,
            'active_banner_themes':active_banner_themes,
            'cart_products':cart_products,
            "totalCartProducts": totalCartProducts,
            **cart_context,
            }

    currency = Currency.objects.get(code='USD')
    response = render(request, template_path, context)
    response.set_cookie('currency', currency.id)
    return response


# def left_slidebar_with_brands(request, brand_id=None):
#     # Your existing code for retrieving cart products, product variants, and other data
#     url = ''
#     # brandid = ()
#     brand = ProBrand.objects.all()
#     category = ProCategory.objects.all()
#     product = ProductVariant.objects.all()

#     if brand_id:
#         brand = ProBrand.objects.get(id=brand_id)
#         product = ProductVariant.objects.filter(variantProduct__productBrand_id=brand)
#         brandList = []
#         brand = []
        
#         for p in product:
#             brandList.append(str(p.variantProduct.productBrand.brandName))
            
#         for b in list(set(brandList)):
#             brand.append(ProBrand.objects.get(brandName=b))
            
        
#         url = reverse('left_slidebar_with_brands', args=[id])
#     # try:
#     #     brand = ProBrand.objects.get(id=brand_id)
#     #     products = ProductVariant.objects.filter(variantProduct__productBrand=brand)
#     # except ProBrand.DoesNotExist:
#     #     return HttpResponse('Invalid Brand ID')
    
#     context = {
#         "ProductsBrand":brand,
#         'url':url,
#         'path':'left_slidebar_with_brands',
#         'products': product, 'ProductsBrand': brand,
#         'productVariant':product,'ProductCategory': category,

#     }
#     return render(request, 'pages/shop/shop-left-sidebar.html',context)

    # Rest of your code for processing the products and rendering the template



def left_slidebar(request,id,brand_id=None):
    url = ''
    # customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    # customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    # wishlist_products = customer_wishlist.wishlistProducts.all()
    # totalWishlistProducts = wishlist_products.count()

    if brand_id:
        try:
            path =request.GET
            full_path = request.get_full_path()
            brandid = ProBrand.objects.get(id=brand_id)
            product = ProductVariant.objects.filter(variantProduct__productBrand_id=brandid)
            brandList = []
            brand = []
            
            for p in product:
                brandList.append(str(p.variantProduct.productBrand.brandName))
                
            for b in list(set(brandList)):
                brand.append(ProBrand.objects.get(brandName=b))
                
            
            url = reverse('left_slidebar_with_brands', args=[id])
        except ProBrand.DoesNotExist:
            return HttpResponse('Invalid Brand ID')
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
    
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)


    context = {"breadcrumb": {"parent": "Product Left Sidebar", "child": "Product Left Sidebar"},
                 "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                #  "Cart": customer_cart,
                # "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
                "cart_products_demo": cart_products_demo,
                "product": product, "products": products,
                "productVariants": productVariants,
                "firstProductVariant": str(firstProductVariant),
                "attributeObjects":attributeObjects,
                "attributeObjectsIds":attributeObjectsIds,
                "images": images,
                "ProductsBrand": brand,
                # "selectedBrand": brandSlug,  # Pass the selected brand_id to the template
                "ProductCategory": category,
                "related_products": related_products,
                "customerReviews":customerReviews,
                "ratingPercentage":ratingPercentage,
                "average_rating":average_rating,
                "rating_range":rating_range,
                "reviewStatus":reviewStatus,
                "last_added_products":last_added_products,  
                "url":url,
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                "totalCartProducts": totalCartProducts,
                **cart_context,
                }
    
    if request.user.is_authenticated:
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
        
    template_path = 'pages/product/product-left-sidebar.html'
    
    response = render(request, template_path, context)
    return response

    # return render(request, 'pages/product/product-left-sidebar.html',context)




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
        
        
def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        customer_wishlist = Wishlist.objects.get(
            wishlistByCustomer=request.user.id)
        customer_wishlist.wishlistProducts.add(id)
        customer_wishlist.save()
    return redirect(request.META['HTTP_REFERER'])


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



def right_sidebar(request,id):
    # customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    # customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    # wishlist_products = customer_wishlist.wishlistProducts.all()
    # totalWishlistProducts = wishlist_products.count()
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalide Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
    
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)


    context = {"breadcrumb": {"parent": "Product Right Sidebar", "child": "Product Right Sidebar"},
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                #  "Cart": customer_cart,
                # "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
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
                "last_added_products":last_added_products,
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                'totalCartProducts': totalCartProducts,
                **cart_context,
                }
    
    return render(request, 'pages/product/product-right-sidebar.html',context)

def no_sidebar(request,id):
    # customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    totalCartProducts = cart_products.count()
    # customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    # wishlist_products = customer_wishlist.wishlistProducts.all()
    # totalWishlistProducts = wishlist_products.count()
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
    
    product = get_object_or_404(Product,id=id)
    selected_delivery_options = product.deliveryOption.all()
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_context = handle_cart_logic(request)



    context = {"breadcrumb": {"parent": "Product No Sidebar", "child": "Product No Sidebar"},
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                #  "Cart": customer_cart,
                # "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
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
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-no-sidebar.html',context)

def bundle(request,id):
    # customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    # cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
    # totalCartProducts = cart_products.count()
    # customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    # wishlist_products = customer_wishlist.wishlistProducts.all()
    # totalWishlistProducts = wishlist_products.count()
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
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
    
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)



    context = {"breadcrumb": {"parent": "Product Bundle", "child": "Product Bundle"},
                "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                #  "Cart": customer_cart,
                # "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
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
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-bundle.html',context)

def image_swatch(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
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
    
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)


    context = {"breadcrumb": {"parent": "Product Image Swatch", "child": "Product Image Swatch"},
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
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-image-swatch.html',context)

def vertical_tab(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
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
    
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)


    context = {"breadcrumb": {"parent": "Product Vertical Tab", "child": "Product Vertical Tab"},
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
                "selected_delivery_options":selected_delivery_options,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-vertical-tab.html',context)

def video_thumbnail(request,id):
    url = ''
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Video Thumbnail", "child": "Product Video Thumbnail"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-video-thumbnail.html',context)

def image_4(request,id):
    url = ''
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product 4 Image", "child": "Product 4 Image"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-4-image.html',context)

def sticky(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    
    context = {"breadcrumb": {"parent": "Product Sticky", "child": "Product Sticky"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    
    return render(request, 'pages/product/product-sticky.html',context)

def accordian(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    

    context = {"breadcrumb": {"parent": "Product Accordian", "child": "Product Accordian"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-page-accordian.html',context)

def product_360_view(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-page-360-view.html',context)

def left_image(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Left Image", "child": "Product Left Image"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-left-image.html',context)

def right_image(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Right Image", "child": "Product Right Image"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-right-image.html',context)

def image_outside(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Image Outside", "child": "Product Image Outside"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,

                }
    return render(request, 'pages/product/product-page-image-outside.html',context)

def thumbnail_left(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Thumbnail Left", "child": "Product Thumbnail Left"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-thumbnail-left.html',context)

def thumbnail_right(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    

    context = {"breadcrumb": {"parent": "Product Thumbnail Right", "child": "Product Thumbnail Right"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-thumbnail-right.html',context)

def thumbnail_bottom(request,id):
    cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
        
    try:
        product = Product.objects.get(id=id)
    except (ValidationError, Product.DoesNotExist):
        return HttpResponse('Invalid Product ID')
    
    products = ProductVariant.objects.all()
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
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
        
    product = get_object_or_404(Product, id=id)
    selected_delivery_options = product.deliveryOption.all()
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Thumbnail Bottom", "child": "Product Thumbnail Bottom"},
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
                "last_added_products":last_added_products,  
                "selected_delivery_options":selected_delivery_options,
                "reviewStatus":reviewStatus,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }
    return render(request, 'pages/product/product-thumbnail-bottom.html',context)


def element_productbox(request):
    ms1 = ProCategory.objects.get(categoryName='ms1')
    subcategories = ms1.get_descendants(include_self=True)
    ms1_products = Product.objects.filter(proCategory__in=subcategories)
    
    ms2 = ProCategory.objects.get(categoryName='ms2')
    subcategories = ms2.get_descendants(include_self=True)
    ms2_products = Product.objects.filter(proCategory__in=subcategories)
    
    ms3 = ProCategory.objects.get(categoryName='ms3')
    subcategories = ms3.get_descendants(include_self=True)
    ms3_products = Product.objects.filter(proCategory__in=subcategories)
    
    ms4 = ProCategory.objects.get(categoryName='ms4')
    subcategories = ms4.get_descendants(include_self=True)
    ms4_products = Product.objects.filter(proCategory__in=subcategories)
    
    ms5 = ProCategory.objects.get(categoryName='ms5')
    subcategories = ms5.get_descendants(include_self=True)
    ms5_products = Product.objects.filter(proCategory__in=subcategories)
    
    vegetables = ProCategory.objects.get(categoryName='Vegetables')
    subcategories = vegetables.get_descendants(include_self=True)
    vegetable_products = Product.objects.filter(proCategory__in=subcategories)
    
    tools = ProCategory.objects.get(categoryName='Tools')
    subcategories = tools.get_descendants(include_self=True)
    tools_products = Product.objects.filter(proCategory__in=subcategories)
    
    pets = ProCategory.objects.get(categoryName='Pets')
    subcategories = pets.get_descendants(include_self=True)
    pets_products = Product.objects.filter(proCategory__in=subcategories)
    
    kids = ProCategory.objects.get(categoryName='Kids')
    subcategories = kids.get_descendants(include_self=True)
    kids_products = Product.objects.filter(proCategory__in=subcategories)
    
    grocery = ProCategory.objects.get(categoryName='Grocery')
    subcategories = grocery.get_descendants(include_self=True)
    grocery_products = Product.objects.filter(proCategory__in=subcategories)
    
    digital_Marketplace = ProCategory.objects.get(categoryName='Digital-Marketplace')
    subcategories = digital_Marketplace.get_descendants(include_self=True)
    digital_Marketplace_products = Product.objects.filter(proCategory__in=subcategories)
    
    furniture = ProCategory.objects.get(categoryName='Furniture')
    subcategories = furniture.get_descendants(include_self=True)
    furniture_products = Product.objects.filter(proCategory__in=subcategories)

    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    
    context = {"breadcrumb": {"parent": "Product Box", "child": "Product Box"},
        'ms1_products':ms1_products,
        'ms2_products':ms2_products,
        'ms3_products':ms3_products,
        'ms4_products':ms4_products,
        'ms5_products':ms5_products,
        'vegetable_products':vegetable_products,
        'tools_products':tools_products,
        'pets_products':pets_products,
        'kids_products':kids_products,
        'grocery_products':grocery_products,
        'digital_Marketplace_products':digital_Marketplace_products,
        'furniture_products':furniture_products,
        'active_banner_themes':active_banner_themes,
        'cart_products':cart_products,
        'totalCartProducts':totalCartProducts,
        **cart_context,
    }
    return render(request, 'pages/product/element-productbox.html',context)

def element_product_slider(request):
    products = Product.objects.all()
    recent_products = Product.objects.all().order_by('-productCreatedAt')[:30]
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Product Slider", "child": "Product Slider"},
               'products':products,
               'recent_products':recent_products,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                **cart_context,
    }
    
    return render(request, 'pages/product/element-product-slider.html',context)

def element_no_slider(request):
    kids = ProCategory.objects.get(categoryName='Kids')
    subcategories = kids.get_descendants(include_self=True)
    kids_products = Product.objects.filter(proCategory__in=subcategories)
    
    pets = ProCategory.objects.get(categoryName='Pets')
    subcategories = pets.get_descendants(include_self=True)
    pets_products = Product.objects.filter(proCategory__in=subcategories)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "No Slider", "child": "No Slider"},
               'kids_products':kids_products,
               'pets_products':pets_products,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                **cart_context,
    }
    return render(request, 'pages/product/element-no_slider.html',context)


# Blog Pages Section

def add_comment(request, id):
    if request.method == 'POST':
        comment = request.POST['comment']
        blog = Blog.objects.get(id=id)
        commentInstance = BlogComment.objects.create(
            commentOfBlog=blog, commentByUser=request.user, comment=comment)
        commentInstance.save()
        return redirect('blog_details', id=id)


def blog_details(request, id):
    try:
        blog = Blog.objects.get(id=id)
    except (ValidationError, Blog.DoesNotExist):
        return HttpResponse('Invalid Blog ID')
    
    blogs = Blog.objects.filter(status=True,blogStatus=1)
    blogCategories = BlogCategory.objects.all()
    blogComments = BlogComment.objects.filter(commentOfBlog__id=id, status=True)
    relatedBlogs = Blog.objects.filter(blogCategory=blog.blogCategory, status=True, blogStatus=1).exclude(id=id)
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    context = {"breadcrumb": {"parent": "Blog Details", "child": "Blog Details"},
                "blog": blog,
                "blogs": blogs,
                "blogCategories": blogCategories,
                "blogComments": blogComments,
                "relatedBlogs": relatedBlogs,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                "totalCartProducts": totalCartProducts,
                **cart_context,
                }
    return render(request, 'pages/blog/blog-details.html',context)


def blog_left_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)
    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    recent_blogs = Blog.objects.all().order_by('-createdAt')[:5]
    popular_blogs = Blog.objects.filter(status=True, popularBlog=1)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)


    context = {"breadcrumb": {"parent": "Blog Left Sidebar", "child": "Blog Left Sidebar"},
               "blogs": blogs,
               "blogCategories": blogCategories,
               "page_obj": page_obj,
               "recent_blogs":recent_blogs,
               "popular_blogs":popular_blogs,
               'active_banner_themes':active_banner_themes,
               'cart_products':cart_products,
                "totalCartProducts": totalCartProducts,
                **cart_context,
               }
    return render(request, 'pages/blog/blog-left-sidebar.html', context)


def blog_right_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)

    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    recent_blogs = Blog.objects.all().order_by('-createdAt')[:5]
    popular_blogs = Blog.objects.filter(status=True, popularBlog=1)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {
        "breadcrumb": {"parent": "Blog Right Sidebar", "child": "Blog Right Sidebar"},
        "blogs": blogs,
        "blogCategories": blogCategories,
        "page_obj": page_obj,
        "recent_blogs":recent_blogs,
        "popular_blogs":popular_blogs,
        'active_banner_themes':active_banner_themes,
        'cart_products':cart_products,
        "totalCartProducts": totalCartProducts,
        **cart_context,
    }
    return render(request, "pages/blog/blog-right-sidebar.html", context)


def blog_no_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {
        "breadcrumb": {"parent": "Blog No Sidebar", "child": "Blog No Sidebar"},
        'blogs':blogs,
        'page_obj':page_obj,
        'active_banner_themes':active_banner_themes,
        'cart_products':cart_products,
        "totalCartProducts": totalCartProducts,
        **cart_context,
    }
    return render(request, 'pages/blog/blog-no-sidebar.html',context)


def blog_creative_left_sidebar(request):
    blogs = Blog.objects.filter(status=True, blogStatus=1)
    paginator = Paginator(blogs, 6)

    blogCategories = BlogCategory.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    recent_blogs = Blog.objects.all().order_by('-createdAt')[:5]
    popular_blogs = Blog.objects.filter(status=True, popularBlog=1)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {
        "breadcrumb": {"parent": "Creative Left Sidebar", "child": "Creative Left Sidebar"},
        "blogs": blogs,
        "blogCategories": blogCategories,
        "page_obj": page_obj,
        "recent_blogs":recent_blogs,
        "popular_blogs":popular_blogs,
        'active_banner_themes':active_banner_themes,
        'cart_products':cart_products,
        "totalCartProducts": totalCartProducts,
        **cart_context,
    }
    return render(request, 'pages/blog/blog-creative-left-sidebar.html',context)



def search_bar(request,params=None):
    query = ''
    data = ''
    products = ProductVariant.objects.all()
    if 'search' in request.GET:
        query = request.GET.get('search')
        if query:
            if params:
                products = products.filter(variantProduct__productName__icontains=query)
                data = [{'id':p.variantProduct.id,'name':p.variantProduct.productName,'category':p.variantProduct.proCategory.categoryName,
                         'brand':p.variantProduct.productBrand.brandName,'description':p.variantProduct.productDescription,}for p in products]
            else:
                products = ProductVariant.objects.all()
                
    products = GetUniqueProducts(products)
    paginator = Paginator(products,8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    context = {"breadcrumb": {"parent": "Search", "child": "Search"}, 'products': products,
                'query': query,'page_obj':page_obj,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                **cart_context,}
    return render(request, 'pages/pages/search.html',context)


def forgot_password(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    if request.method == 'POST':
        email = request.POST['emailname']
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            otp = generateOTP()
            message = render_to_string('authentication/reset_password_email.html',{
                'user':user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':otp,
            })
            to_email = email
            mail = EmailMultiAlternatives(mail_subject,message,to=[to_email])
            mail.attach_alternative(message, "text/html")
            mail.send()
            temDataObject = TemporaryData.objects.get(TemporaryDataByUser__email=email)
            temDataObject.otpNumber = otp
            
            current_time = datetime.now()
            temDataObject.otpExpiryTime = current_time + timedelta(minutes=1)
            temDataObject.save(update_fields=['otpNumber','otpExpiryTime'])
            
            response = HttpResponseRedirect('verify_token')
            response.set_cookie('code',user.id,max_age=180)
            messages.success(request,'An OTP has been sent to your email adress successfully')
            return response
        else:
            messages.error(request,'Account Does Not Exist!')
            return redirect('forgot_password')
            
    return render(request, 'authentication/forget-pwd.html',{'active_banner_themes':active_banner_themes})
    
    
def verify_token(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        get_id = request.COOKIES['code']
        get_user = CustomUser.objects.get(id=get_id)
        
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
            messages.error(request,'Your otp has been expired! Please regenerate otp.')
            return redirect('forgot_password')
    return render(request,'authentication/verify-token.html' ,{'active_banner_themes':active_banner_themes})

def update_password(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    if request.method == "POST":
        password = request.POST['newpass']
        conf_password = request.POST['confnewpass']
        
        password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        
        user = CustomUser.objects.get(username__exact=request.user.username)

        if password and conf_password:
            if not re.search(password_pattern,password):
                messages.warning(request, 'Password must be at least 8 characters long and contain at least one letter and one number')
                return redirect('update_password')
            
            if password == conf_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('login_page')
            else:
                messages.error(request,'Password Does Not Match')
                return redirect('update_password')
    context = {"breadcrumb": {"parent": "Update password", "child": "Update password"},
               'active_banner_themes':active_banner_themes,
    }
    return render(request, 'authentication/update_password.html',context)  


def user_dashboard(request):
    wishlist_products = None
    totalWishlistProducts = None
    if request.user.is_authenticated:
        customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
        cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
        totalCartProducts = cart_products.count()

        try:
            customer_wishlist = Wishlist.objects.get(
                wishlistByCustomer=request.user.id)
            wishlist_products = customer_wishlist.wishlistProducts.all()
            totalWishlistProducts = wishlist_products.count()
        except Wishlist.DoesNotExist:
            customer_wishlist = None

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
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Dashboard"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "totalorder": totalorder, "pendingOrders": pendingOrders,
               "orderaillingaddress": orderaillingaddress, "products": products,
               "orders": orders, "lastAddress": lastAddress,
               "userId": request.user.id,
                'active_banner_themes':active_banner_themes,
                **cart_context,
            }
    return render(request, 'pages/pages/account/dashboard.html',context)

def profile(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    context = {"breadcrumb":{"parent":"profile","child":"profile"},
               'active_banner_themes':active_banner_themes,
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
               **cart_context,
               }
    return render(request, 'pages/pages/account/profile.html',context)


def save_address(request):
    if request.method == "POST":
        body = json.loads(request.body)
        addressId = body['addressId']
        addressGet = OrderBillingAddress.objects.get(id=addressId)
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
    user = OrderBillingAddress.objects.create(customer=customer,customerFirstName=fname, customerLastName=lname, customerUsername=username, customerEmail=email, customerMobile=mobno,customerAddress1=address1,customerAddress2=address2, customerCountry=country, customerCity=city, customerZip =zipcode)
    user.save()
    return HttpResponse(request,status=200)

def remove_address(request,id):
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
                messages.warning(request, 'Address cannot be removed as it is associated with a delivered order')
                return redirect('user_dashboard')
        else:
            address.delete()
            messages.success(request,'Address Removed Successfully')
            return redirect('user_dashboard')
    else:
        address.delete()
        messages.success(request,"Address Removed Successfully")
        return redirect('user_dashboard')

def get_address(request):
    if request.method == "POST":
        body = json.loads(request.body)
        addressId = body['addressId']
        address = OrderBillingAddress.objects.get(id=addressId)
        data = {'fname':address.customerFirstName, 'lname':address.customerLastName, 'username':address.customerUsername, 'email':address.customerEmail, 'mobno':address.customerMobile, 'address1':address.customerAddress1, 'address2':address.customerAddress2, 'country':address.customerCountry,'city':address.customerCity,'zipcode':address.customerZip}
        return JsonResponse(data,safe=False)


def change_password(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    
    if not request.user.is_authenticated:
        messages.warning(request, 'You need to login first.')
        return redirect('login_page')
    
    if request.method == "POST":
        current_password = request.POST['currentpass']
        new_password = request.POST['newpass']
        confirm_password = request.POST['confnewpass']
        user = CustomUser.objects.get(username__exact=request.user.username)
            
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password changed successfully')
                return redirect('login_page')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'Password Does Not Match')
            return redirect('change_password')
        
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
            
    context = {"breadcrumb":{"parent": "Change password", "child":"Change password"},
               'active_banner_themes':active_banner_themes,
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
               **cart_context,
               }
    return render(request, 'authentication/change_password.html',context)


def contact_us(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    if request.method == "POST":
        firstname = request.POST['first']
        lastname = request.POST['last']
        email = request.POST['email']
        number = request.POST['number']
        comment = request.POST['comment']
        name = str(firstname)+" "+str(lastname)
        
        if ContactUs.objects.filter(contactUsEmail=email).exists():
            messages.warning(request, 'Email already exists')
        else:
            user = ContactUs.objects.create(contactUsName=name,contactUsEmail=email,contactUsNumber=number,contactUsComment=comment)
            user.save()
            messages.success(request, 'Your form has been submitted successfully')
            return redirect('contact_us')
        
    context = {"breadcrumb":{"parent":"Contact","child":"Contacts"},
               'active_banner_themes':active_banner_themes,
               'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                **cart_context,
               }
    return render(request, 'pages/pages/account/contact.html',context)

def get_subcategories(category,parent=True):
    try:
        fashion_category = ProCategory.objects.get(categoryName__iexact=category)
        subcategories = ProCategory.objects.filter(Q(parent=fashion_category) & Q(parent=parent))
        
        result = []
        for subcategory in subcategories:
            subcategory_data = {
                'id': subcategory.id,
                'name': subcategory.categoryName,
                'subcategories': get_subcategories(subcategory.categoryName, parent=True)
            }
            result.append(subcategory_data)
        
        return result
    except ProCategory.DoesNotExist:    
        return []


def search_products(request):
    query = request.GET.get('q','')
    category = request.GET.get('category','')
    
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
                'category': product.variantProduct.proCategory.categoryName,
                } for product in products]
    return JsonResponse({'status': 200, 'data': results})


def get_category_ids(data):
    category_ids = []
    for category in data:
        category_ids.append(category['id'])
        category_ids.extend(get_category_ids(category['subcategories']))
    return category_ids


@csrf_exempt
def quick_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        productId = body["productId"]
        productVariantId = body["productVariantId"]
        
        product = Product.objects.get(id=productId)
        productVariant = ProductVariant.objects.get(id=productVariantId)
        firstProductVariant = ProductVariant.objects.filter(variantProduct=product).first()
        multipleImages = MultipleImages.objects.filter(multipleImageOfProduct=product)
        multipleImgList = []
        
        for image in multipleImages:
            multipleImgList.append(str(image.multipleImages.url))
            
        singleImage = str(productVariant.variantProduct.productImageFront)
        
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
        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie('cart', cart_items_json)
        return response
    
def get_total_tax_values(variant_products):
    TotalVariantTax = 0
    TotalVariantTaxPrice = 0
    TotalVariantFinalPriceAfterTax = 0

    for variant_product in variant_products:
        try:
            variant = ProductVariant.objects.get(id = variant_product['variant_id'])
            TotalVariantTax += variant.productVariantTax * int(variant_product['quantity'])
            TotalVariantTaxPrice += variant.productVariantTaxPrice * int(variant_product['quantity'])
            TotalVariantFinalPriceAfterTax += variant.productVariantFinalPriceAfterTax * int(variant_product['quantity'])
        except ObjectDoesNotExist:  
            TotalVariantTax += 0
            TotalVariantTaxPrice += 0
            TotalVariantFinalPriceAfterTax += 0
            # Handle the case where the ProductVariant does not exist
            print(f"ProductVariant with id {variant_product['variant_id']} does not exist.")

        
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
                        "taxPrice":cart.getTotalTax,
                    }
                    return JsonResponse(data, safe=False)
                else:
                    cartTotalPrice = cart.getTotalPrice
                    cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
                    data = {
                        "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
                        "cartTotalPrice": cartTotalPrice,
                        "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
                        "taxPrice":cart.getTotalTax,
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
            
        # Inside your Django view


        if actionType == "plus" and cart_products:
            print('=======>Inside plus condition <==========')
            for item in cart_products:
                if str(id) == item['variant_id'] and str(product_id) == item['product_id']:
                    item['quantity'] = int(item['quantity']) + 1
                    item['totalPrice'] = format(item['quantity'] * item['price'],".2f")

        if actionType == "minus" and cart_products:
            print('=======>Inside minus condition <==========')
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
                    "taxPrice":TotalTaxPrice,
                    "cartTotalPriceAfterTax": TotalFinalPriceAfterTax,
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
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    context = {"breadcrumb": {"parent": "Cart", "child": "Cart"},
               'active_banner_themes':active_banner_themes,
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
    
    return render(request, 'pages/pages/account/cart.html',context)


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


def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        try:
            customer_wishlist = Wishlist.objects.get(
                wishlistByCustomer=request.user.id)
            customer_wishlist.wishlistProducts.add(id)
            customer_wishlist.save()
        except Wishlist.DoesNotExist:
            customer_wishlist = None
    else:
        return redirect('login_page')
    return redirect(request.META['HTTP_REFERER'])



def wishlist_page(request):
    totalCartProducts = 0
    wishlist_products = None
    totalWishlistProducts = 0
    if request.user.is_authenticated:
        try:
            customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
            cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
            totalCartProducts = cart_products.count()

            customer_wishlist = Wishlist.objects.get(
                wishlistByCustomer=request.user.id)
            wishlist_products = customer_wishlist.wishlistProducts.all()
            wishlist_product = customer_wishlist.wishlistProducts.first()

            totalWishlistProducts = wishlist_products.count()
        except Wishlist.DoesNotExist:
            customer_wishlist = None
    else:
        return redirect('login_page')
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": "Wishlist", "child": "Wishlist"},
               "totalCartProducts": totalCartProducts,
               "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
                'active_banner_themes':active_banner_themes,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                **cart_context,
}

    return render(request, 'pages/pages/account/wishlist.html', context)


def delete_wishlist_product(request,id):
    referer = request.META.get('HTTP_REFERER', None)
    customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
    customer_wishlist.wishlistProducts.remove(id)
    customer_wishlist.save()
    messages.success(request,'Product Removed Successfully')
    return redirect(referer)


def add_to_cart_from_wishlist(request, id, quantity):
    referer = request.META.get('HTTP_REFERER', None)
    # Product moved from wishlist to cart)
    product = ProductVariant.objects.get(id=id)
    cartObject = Cart.objects.get(cartByCustomer=request.user.id)
    
    if product.productVariantQuantity > 0:
        if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=product).exists():
            cartProductObject = CartProducts.objects.get(cartByCustomer=request.user, cartProduct=product)
            cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + int(quantity)
            cartProductObject.save()

            # Product remove from wishlist
            customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
            customer_wishlist.wishlistProducts.remove(id)
            customer_wishlist.save()
            return redirect(referer)
        else:
            CartProducts.objects.create(
                cart=cartObject,cartProduct=product, cartProductQuantity=quantity).save()

            # Product remove from wishlist
            customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
            customer_wishlist.wishlistProducts.remove(id)
            customer_wishlist.save()
            return redirect(referer)
        # CartProducts.objects.create(cartProduct=product,cartProductQuantity=1).save()
    else:
        messages.success(request, 'Product out of stock.')
        return redirect(referer)


        


def user_authenticate(request):
    is_authenticated = request.user.is_authenticated
    data = {'is_authenticated': is_authenticated}
    return JsonResponse(data)

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
    
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))


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
        couponObj = coupon.first()
        couponAmount = 0
        
        if len(coupon) == 1:
            couponStatus = True
            couponUsesByCustomer = CouponHistory.objects.filter(coupon=couponObj)
            if len(couponUsesByCustomer) < couponObj.usageLimit and int(couponObj.numOfCoupon) > 0:
                currentDateTime = timezone.now()
                if couponObj.expirationDateTime >= currentDateTime and price >= couponObj.minAmount:
                    if couponObj.couponType == "Fixed":
                        couponAmount = int(couponObj.couponDiscountOrFixed)
                    if couponObj.couponType == "Percentage":
                        couponDiscountAmount = ((price*couponObj.couponDiscountOrFixed)/100)
                        couponAmount = couponDiscountAmount

        couponAmountForUSD = couponAmount
        currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))    
        couponAmount = couponAmount * currency.factor
        finalAmount = (price-couponAmount)+(tax*currency.factor)
        finalAmountInUSD = finalAmountInUSD-couponAmountForUSD
        
        data = {'valid':couponStatus,'couponAmount':couponAmount,'currencySymbol':currency.symbol,
                'finalAmount':finalAmount,'finalAmountInUSD':finalAmountInUSD}
        return JsonResponse(data, safe=False)
    
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
   
@login_required(login_url='login_page')
def checkout_page(request):
    customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
    cart_products_demo = serializers.serialize("json",CartProducts.objects.filter(cartByCustomer=request.user.id))
    
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
        couponObj = coupon.first()

        if len(coupon) == 1:
            couponUsesByCustomer = CouponHistory.objects.filter(coupon=couponObj)
            if len(couponUsesByCustomer) < couponObj.usageLimit and int(couponObj.numOfCoupon) > 0:
                currentDateTime = timezone.now()
                if couponObj.expirationDateTime >= currentDateTime and getTotalPrice >= couponObj.minAmount:
                    if couponObj.couponType == "Fixed":
                        couponAmount = int(couponObj.couponDiscountOrFixed)
                    if couponObj.couponType == "Percentage":
                        couponDiscountAmount = ((getTotalPrice*couponObj.couponDiscountOrFixed)/100)
                        couponAmount = couponDiscountAmount
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
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    
    print('PAYPAL_CLIENT_ID ======>',settings.PAYPAL_CLIENT_ID)
    
    context = {"breadcrumb": {"parent": "Checkout", "child": "Checkout"},
               "Cart": customer_cart,'cart_products':cart_products,'totalCartProducts':totalCartProducts,
               "wishlist":customer_wishlist, "wishlist_products":wishlist_products,"totalWishlistProducts":totalWishlistProducts,
               "cart_products_demo":cart_products_demo,
               "getTotalTax":getTotalTax,
               "getFinalPriceAfterTax":finalAmount,
               "getTotalPrice":getTotalPrice,
               "couponAmount":couponAmount,
               "billingAddresses":billingAddresses,
               "payment":payment,
               "rsk": settings.RAZORPAY_KEY_ID,
               "ppl":settings.PAYPAL_CLIENT_ID,
               **cart_context,
               'active_banner_themes':active_banner_themes,

               }
    
    return render(request, 'pages/pages/account/checkout.html',context)


def payment_complete(request):
    body = json.loads(request.body)
    
    if 'addressId' in body:
        addressId = body["addressId"]
        strPrice = body["price"]

        decimalPrice = Decimal(strPrice)
        price = convert_amount_based_on_currency(decimalPrice,request)
        cartid = body["cartid"]
        orderpaymentmethodname = body["orderpaymentmethodname"]

        cookie_value = request.COOKIES.get('couponCode')
        if cookie_value:
            couponCode = cookie_value
        else:
            couponCode = ''
        
        couponDiscountAmount = 0
        createHistory = False
        if couponCode:
            try:
                coupon = Coupon.objects.get(couponCode = couponCode)
                couponUsesByCustomer = CouponHistory.objects.filter(coupon=coupon)
                if len(couponUsesByCustomer) < coupon.usageLimit and int (coupon.numOfCoupon) > 0:
                    currentDateTime = timezone.now()
                    if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
                        if coupon.couponType == "Fixed":
                            price = price-int(coupon.couponDiscountOrFixed)
                        if coupon.couponType == "Percentage":
                            couponDiscountAmount = ((price*coupon.couponDescription)/100)
                            price = price-couponDiscountAmount
                        createHistory = True
            except:
                pass
        
        order_billing_address_instance = OrderBillingAddress.objects.get(id=addressId)
        paymentmethod = PaymentMethod.objects.get(paymentMethodName=orderpaymentmethodname)
        
        if 'rpPaymentId' in body:
            rpPaymentId = body['rpPaymentId']
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=rpPaymentId, orderAmount=price, orderPaymentMethodName=paymentmethod,)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()

            if createHistory:
                coupon.numOfCoupon = coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon, couponHistoryByUser=order_instance.orderedByCustomer, couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_coupon = request.COOKIES.get('couponCode')
            if remove_coupon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response
            return JsonResponse(data={'message':'Payment completed'},safe=False)
        

        if 'payPalTransactionID' in body:
            payPalTransactionID = body["payPalTransactionID"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=payPalTransactionID, orderAmount=price, orderPaymentMethodName=paymentmethod,)
            order_payment_instance.save()
            cart = Cart.objects.get(id=cartid)
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, OrderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings = cart.getTotalDiscountAmount)
            order_instance.save()
            
            # Create the history for this transaction

            if createHistory:
                coupon.numOfCoupon = coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon, couponHistoryByUser=order_instance.orderedByCustomer, couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_coupon = request.COOKIES.get('couponCode')
            if remove_coupon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response
            return JsonResponse(data={'message': 'Payment Completed'},safe=False)
    else:
        strPrice = body["price"]
        decimalPrice = Decimal(strPrice)
        price = convert_amount_based_on_currency(decimalPrice,request)
        fname = body["fname"]
        lname = body["lname"]
        uname = body["uname"]
        email = body["email"]
        address1 = body["address1"]
        country = body["country"]
        city = body["city"]
        zip = body["zip"]
        cartid = body["cartid"]
        orderpaymentmethodname = body["orderpaymentmethodname"]
        
        cookie_value = request.COOKIES.get('couponCode')
        if cookie_value:
            couponCode = cookie_value
        else:
            couponCode = ''
        
        couponDiscountAmount = 0
        createHistory = False
        if couponCode:
            try:
                coupon = Coupon.objects.get(couponCode=couponCode)
                couponUsesByCustomer = CouponHistory.objects.filter(coupon=coupon)
                if len(couponUsesByCustomer) < coupon.usageLimit and int(coupon.numOfCoupon) > 0:
                    currentDateTime = timezone.now()
                    if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
                        if coupon.couponType == "Fixed":
                            price = price-int(coupon.couponDiscountOrFixed)
                        if coupon.couponType == "Percentage":
                            couponDiscountAmount = ((price*coupon.couponDiscountOrFixed)/100)
                            price = price-couponDiscountAmount
                        createHistory = True
            except:
                pass
        order_billing_address_instance = OrderBillingAddress.objects.create(customer=request.user, customerFirstName=fname, customerLastName=lname, customerUserName=uname,
                                                                            customerEmail=email, customerAddress1=address1, customerCountry=country, customerCity=city, customerZip=zip)
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
                coupon.numOfCoupon = coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon, couponHistoryByUser=order_instance.orderedByCustomer, couponHistoryByOrder=order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_coupon = request.COOKIES.get('couponCode')
            if remove_coupon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response
            return JsonResponse(data={'message':'Payment completed'},safe=False) 
        

        
        if 'payPalTransactionID' in body:
            payPalTransactionID = body["payPalTransactionID"]
            order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user,
                                                                 orderPaymentTransactionId=payPalTransactionID,
                                                                 orderAmount=price, orderPaymentMethodName=paymentmethod)
            order_payment_instance.save()      
            cart = Cart.objects.get(id=cartid)                                                           
            order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, OrderBillingAddress=order_billing_address_instance,
                                                  orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
            order_instance.save()
            
            # Create the history for this transaction
            
            if createHistory:
                coupon.numOfCoupon = coupon.numOfCoupon-1
                coupon.save()
                CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder = order_instance)
            CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
            remove_coupon = request.COOKIES.get('couponCode')
            if remove_coupon:
                response = HttpResponse("Currency removed")
                response.delete_cookie('couponCode')
                return response
            return JsonResponse(data={'message':'Payment completed'},safe=False)

    
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
        print('order=======++>',order)
        if order is not None:
            paymentmethod = order.orderPayment.orderPaymentMethodName
            products = ProductOrder.objects.filter(productOrderOrderId=order.id)
        else:
            paymentmethod = None
            products = []
    else:
        return redirect('login_page')
    
    
    print('products on order ====>',products)
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    context = {
        "breadcrumb": {"parent": "Order-Success", "child": "Order-Success"},
        "Cart":customer_cart,"cart_products":cart_products, 'totalCartProducts':totalCartProducts,
        "wishlist":customer_wishlist, "wishlist_products":wishlist_products,'totalWishlistProducts':totalWishlistProducts,
        "orderid": order.id if order else None,
        "transactionId":order.orderPayment.orderPaymentTransactionId if order else None,
        "orderdate":order.orderCreatedAt if order else None,
        "orderprice":order.orderTotalPrice if order else None,
        "orderTax": order.orderTotalTax if order else None,
        "ordersubtotal":order.orderPrice if order else None,
        "products":products if order else None,
        "orderaddress":order.orderBillingAddress if order else None,
        "contactno":customer.customerContact,
        "paymentmethod":paymentmethod if order else None,
        'active_banner_themes':active_banner_themes,
    }
    
    return render(request, 'pages/pages/order-success.html',context)


def checkout_2_page(request):
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)
    context = {"breadcrumb": {"parent": "Checkout-2", "child": "Checkout-2"},
               'cart_products':cart_products,
               'totalCartProducts':totalCartProducts,
               **cart_context,
               }
    return render(request,'pages/pages/account/checkout2.html',context)


def compare_page(request):
    wishlist_products = None
    totalWishlistProducts = None 
    compare_products = None
    
    if request.user.is_authenticated:
        try:
            customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
            cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
            totalCartProducts = cart_products.count()
        except Cart.DoesNotExist:
            customer_cart = None
            
        try:    
            customer_wishlist = Wishlist.objects.get(
                wishlistByCustomer=request.user.id)
            wishlist_products = customer_wishlist.wishlistProducts.all()
            totalWishlistProducts = wishlist_products.count()
        except Wishlist.DoesNotExist:
            customer_wishlist = None
            
        try:
            customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
            compare_products = customer_compare.compareProducts.all()
        except Compare.DoesNotExist:
            customer_compare = None
            
    else:
        return redirect('login_page')
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    context = {"breadcrumb": {"parent": "Compare", "child": "Compare"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "compare": customer_compare, "compare_products": compare_products,
                'active_banner_themes':active_banner_themes,
}
    return render(request, 'pages/pages/compare/compare.html', context)

def compare_page2(request):
    wishlist_products = None
    totalWishlistProducts = None 
    compare_products = None
    
    if request.user.is_authenticated:
        try:
            customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
            cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
            totalCartProducts = cart_products.count()
        except Cart.DoesNotExist:
            customer_cart = None
            
        try:
            customer_wishlist = Wishlist.objects.get(
                wishlistByCustomer=request.user.id)
            wishlist_products = customer_wishlist.wishlistProducts.all()
            totalWishlistProducts = wishlist_products.count()
        except Wishlist.DoesNotExist:
            customer_wishlist = None
            
        try:
            customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
            compare_products = customer_compare.compareProducts.all()
        except Compare.DoesNotExist:
            customer_compare = None
            
    else:
        return redirect('login_page')
    
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    context = {"breadcrumb": {"parent": "Compare-2", "child": "Compare-2"},
               "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
               "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
               "compare": customer_compare, "compare_products": compare_products,
                'active_banner_themes':active_banner_themes,
    }
    return render(request, 'pages/pages/compare/compare-2.html',context)



def compare_products(request, id):
    if request.user.is_authenticated:
        customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
        customer_compare.compareProducts.add(id)
        customer_compare.save()
        return HttpResponse(status=204)
    else:
        return redirect('login_page')
    
def delete_compare_product(request,id):
    customer_compare = Compare.objects.get(compareByCustomer=request.user.id)
    customer_compare.compareProducts.remove(id)
    customer_compare.save()
    referer_url = request.META.get('HTTP_REFERER', 'compare_page')
    return redirect(referer_url)


            
def user_authenticate(request):
    is_authenticated = request.user.is_authenticated
    data = {'is_authenticated': is_authenticated}
    return JsonResponse(data)

def page_not_found(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)

    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": 404, "child": 404},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }

    return render(request, 'pages/pages/404.html', context)


def faq_page(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_products,totalCartProducts = show_cart_popup(request)
    cart_context = handle_cart_logic(request)

    context = {"breadcrumb": {"parent": 'FAQ', "child": 'FAQ'},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,
                'active_banner_themes':active_banner_themes,
                **cart_context,
                }

    return render(request,'pages/pages/faq.html',context)

def coming_soon(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
    context = {"breadcrumb": {"parent": "Coming Soon", "child": "Coming Soon"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'pages/pages/coming-soon.html', context)



def about_page(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {"breadcrumb":{"parent":"About","child":"About"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'pages/pages/about-page.html',context)


def review(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)

    context = {"breadcrumb":{"parent":"Review","child":"Review"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'pages/pages/review.html',context)


def typography(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
    context = {"breadcrumb":{"parent":"TYPOGRAPHY","child":"TYPOGRAPHY"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'pages/pages/typography.html',context)

def look_book(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
    context = {"breadcrumb":{"parent":"Look book","child":"Look book"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,
                }
    return render(request, 'pages/pages/look-book.html',context)

def collection(request):
    active_banner_themes = BannerTheme.objects.filter(is_active=True)
    cart_context = handle_cart_logic(request)
    cart_products,totalCartProducts = show_cart_popup(request)
    context = {"breadcrumb":{"parent":"collection","child":"collection"},
                'active_banner_themes':active_banner_themes,
                **cart_context,
                'cart_products':cart_products,
                'totalCartProducts':totalCartProducts,}
    return render(request, 'pages/pages/collection.html',context)

@login_required(login_url='login_page')
def cart_to_checkout_validation(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            body = json.loads(request.body)
            cartId = body["cartId"]
            cart = Cart.objects.get(id=cartId)
            cartProducts = CartProducts.objects.filter(cart=cart)
            productList = []
            flag = False
            for product in cartProducts:
                dbProduct = ProductVariant.objects.get(id=product.cartProduct.id)
                if product.cartProductQuantity <= dbProduct.productVariantQuantity:
                    pass
                else:
                    productList.append({"productName":str(product.cartProduct.variantProduct.productName),"outOfStockProducts":str(product.cartProduct.productVariantQuantity)})
            if len(productList) > 0:
                flag=True
                
            if flag:
                data = {"outOfStockProducts":productList,"flag":str(flag),}
                response = JsonResponse(data,safe=False)
                expiry_time = datetime.utcnow() + timedelta(seconds=30)
                response.set_cookie('checkout','False',expires=expiry_time)
                return response
            else:
                data = {"outOfStockProducts":productList, "flag":str(flag),}
                response = JsonResponse(data,safe=False)
                expiry_time = datetime.utcnow() + timedelta(seconds=30)
                response.set_cookie("checkout",'True',expires=expiry_time)
                return response
    else:
        return redirect('login_page')
    






