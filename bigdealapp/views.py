from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from accounts.models import CustomUser
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import auth
from .models import Banner,BannerTheme,BannerType,Blog
from product.models import (AttributeName, MultipleImages, ProBrand, ProCategory, Product,
                            ProductAttributes, ProductReview, ProductVariant,AttributeValue,ProductMeta)

from currency.models import Currency

import json





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
    print('currencyID ============>',currencyID)
    response = HttpResponse('Cookie Set for currency')
    response.set_cookie('currency', currencyID)
    return response


def get_selected_currency(request):
    currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
    data = {"factor": currency.factor, "symbol": currency.symbol}
    return JsonResponse(data, safe=False)


def signup_page(request):
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
        context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"}}
        return render(request, 'authentication/sign-up.html', context)
                    

def login_page(request):
    if request.method == "POST":
        username = request.POST['name']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None and user.is_customer:
            auth.login(request,user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login_page')
    context = {"breadcrumb": {
         "parent": "Dashboard", "child": "Default"}}
    return render(request, 'authentication/login.html',context)

def logout_page(request):
    auth.logout(request)
    return redirect('/login_page')


# HOME PAGES SECTION 

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
        

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbrands':brands,
               'allbanners':banners,
               'layout1_products':layout1_products,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'col_banner':col_banner,
               }
    return render(request,'pages/home/ms1/index.html',context)

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

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
                'both_banners':both_banners,
               'layout2_products':layout2_products,
               'media_banners':media_banners,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'blogs':blogs,
               }

    return render(request, 'pages/home/ms2/layout-2.html',context)

def layout3(request):
    return render(request, 'pages/home/ms3/layout-3.html')

def layout4(request):   
    return render(request, 'pages/home/ms4/layout-4.html')

def megastore(request):
    return render(request, 'pages/home/ms5/megastore.html')

def layout5(request):
    return render(request, 'pages/home/electronics/layout-5.html')

def layout6(request):
    return render(request, 'pages/home/vegetables/layout-6.html')

def furniture(request):
    return render(request, 'pages/home/furniture/furniture.html')

def cosmetic(request):
    return render(request,'pages/home/cosmetic/cosmetic.html')

def kids(request):
    return render(request, 'pages/home/kids/kids.html')











# SHOP PAGES SECTION 

def shop_left_sidebar(request):
    return render(request, 'pages/shop/shop-left-sidebar.html')

def shop_right_sidebar(request):
    return render(request, 'pages/shop/shop-right-sidebar.html')

def shop_no_sidebar(request):
    return render(request, 'pages/shop/shop-no-sidebar.html')

def shop_sidebar_popup(request):
    return render(request, 'pages/shop/shop-sidebar-popup.html')

def shop_metro(request):
    return render(request, 'pages/shop/shop-metro.html')

def shop_full_width(request):
    return render(request, 'pages/shop/shop-full-width.html')

def shop_infinite_scroll(request):
    return render(request, 'pages/shop/shop-infinite-scroll.html')

def shop_3grid(request):
    return render(request, 'pages/shop/shop-3-grid.html')

def shop_6grid(request):
    return render(request, 'pages/shop/shop-6-grid.html')

def shop_list_view(request):
    return render(request, 'pages/shop/shop-list-view.html')

def tools(request):
    return render(request, 'pages/home/tools/tools.html')

def grocery(request):
    return render(request, 'pages/home/grocery/grocery.html')

def pets(request):
    return render(request, 'pages/home/pets/pets.html')

def farming(request):
    return render(request, 'pages/home/farming/farming.html')

def digital_marketplace(request):
    return render(request, 'pages/home/digital_marketplace/digital-marketplace.html')


