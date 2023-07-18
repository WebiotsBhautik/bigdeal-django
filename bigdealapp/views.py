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
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore3 Demo')
    # shop_banners = banners.filter(bannerType__bannerTypeName='Banner')
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
        
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
               'layout3_products':layout3_products,
               'media_banners':media_banners,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
               'left_banners':left_banners,
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

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
               'media_banners':media_banners,
               'layout4_products':layout4_products,
               'subcategories':subcategories,
               'products_by_subcategory':products_by_subcategory,
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
            'main_categories':main_categories,
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

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'allbrands':brands,
            'electronics_category':electronics_category,
            'electronics_products':electronics_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'media_banners':media_banners,
            'blogs':blogs,
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

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'vegetable_category':vegetable_category,
            'vegetable_products':vegetable_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'four_banner':four_banner,
            'five_banner':five_banner,
            'six_banner':six_banner,
            }

    return render(request, 'pages/home/vegetables/vegetable.html',context)

def furniture(request):
    return render(request, 'pages/home/furniture/furniture.html')

def cosmetic(request):
    return render(request,'pages/home/cosmetic/cosmetic.html')

def kids(request):
    return render(request, 'pages/home/kids/kids.html')

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



