from django.shortcuts import render
from django.core.paginator import Paginator
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

from bigdealapp.helpers import get_color_and_size_list, get_currency_instance, GetUniqueProducts, IsVariantPresent, GetRoute, create_query_params_url, generateOTP, get_product_attribute_list, get_product_attribute_list_for_quick_view, search_query_params_url, convert_amount_based_on_currency


from currency.models import Currency
from decimal import Decimal, ROUND_HALF_UP
from django.http import Http404
import json
import uuid





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
            response = HttpResponseRedirect('index')
            currency = Currency.objects.get(code='USD')
            response.set_cookie('currency', currency.id)
            return response
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
        
    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'furniture_category':furniture_category,
            'furniture_products':furniture_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
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

        
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'last_two_banners':last_two_banners,
            'cosmetic_category':cosmetic_category,
            'cosmetic_products':cosmetic_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
           'first_banner':first_banner,
           'second_banner':second_banner,
           'third_banner':third_banner,
           'fourth_banner':fourth_banner,
           
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
        

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
        #     'last_two_banners':last_two_banners,
            'kids_category':kids_category,
            'kids_products':kids_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
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
                                            
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'tools_category':tools_category,
            'tools_products':tools_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'last_three_collection':last_three_collection,
            'blogs':blogs,
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
    

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'grocery_category':grocery_category,
            'grocery_products':grocery_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            'five_banner':five_banner,
            'six_banner':six_banner,
            'last_testimonial':last_testimonial,
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

    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
            'allbanners':banners,
            'mainslider':mainslider,
            'pets_category':pets_category,
            'pets_products':pets_products,
            'subcategories':subcategories,
            'products_by_subcategory':products_by_subcategory,
            'blogs':blogs,
            'first_banner':first_banner,
            'second_banner':second_banner,
            'third_banner':third_banner,
            'fourth_banner':fourth_banner,
            # 'five_banner':five_banner,
            # 'six_banner':six_banner,
            # 'last_testimonial':last_testimonial,
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
            'sale_banner':sale_banner,
            'counter_banner':counter_banner,
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
        }
    return render(request, 'pages/home/digital_marketplace/digital-marketplace.html',context)






# SHOP PAGES SECTION 

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
    
    # product_variants = ProductVariant.objects.select_related('product').order_by('-product__productCreatedAt')
    # last_added_products = product_variants[:9]

    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
        
        
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
            # 'categoryid':categoryid,
            # 'rating_range':rating_range,
            # 'discount_filters':discount_filters,
            # 'selected_prices':selected_allprice,
            # 'selected_discounts':selected_alldiscount,                           
            'path':'left-sidebar',
            'totalCount':totalProduct,
            # 'min_price':min_price*selected_currency.factor,
            # 'max_price':max_price*selected_currency.factor,
            }
    return render(request, 'pages/shop/shop-left-sidebar.html',context)

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

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
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
            'path':'right-sidebar',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-right-sidebar.html',context)

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

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
    
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
            'path':'no-sidebar',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-no-sidebar.html',context)

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

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
    
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
            'path':'no-sidebar',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-sidebar-popup.html',context)

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
    # collection_banner  = banners.filter(bannerType__bannerTypeName='Shop metro')

    
    last_added_products = Product.objects.all().order_by('-productCreatedAt')[:9]
    
    
    shop_bnr = BannerType.objects.get(bannerTypeName='Shop category banner')
    shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
    
    sidebar_bnr = BannerType.objects.get(bannerTypeName='side-bar banner')
    sidebar_banner = Banner.objects.filter(bannerType=sidebar_bnr).first()

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
    
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
            'path':'Shop Metro',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-metro.html',context)

def shop_full_width(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore1 Demo')
    context = {"breadcrumb": {"parent": "Shop Full Width", "child": "Shop Full Width"},
            'allbanners': banners,
            }
    return render(request, 'pages/shop/shop-full-width.html',context)

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

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
    
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
            'path':'Shop infinite scroll',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-infinite-scroll.html',context)

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

    
    
    if selected_allprice:
        price = selected_allprice.split(',')
        price_filter = product
        current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
        factor = current_currency.factor
        product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))

    if selected_allbrand:
        brand_filter = product
        x = selected_allbrand.split(',')
        y = x[:-1]
        product = []
        for brands in y:
            product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
            product += product1
            
            
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
        
    try:
        currency_id = request.COOKIES.get('currency', None)
        if currency_id and uuid.UUID(currency_id):
            selected_currency = Currency.objects.get(id=currency_id)
            if product and selected_currency:
                min_price = min_price*selected_currency.factor
                max_price = max_price*selected_currency.factor
        else:
            pass
    except Currency.DoesNotExist:
        pass
    except ValueError:
        pass
    
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
            'path':'Shop 3grid',
            'totalCount':totalProduct,
            }
    return render(request, 'pages/shop/shop-3-grid.html',context)

def shop_6grid(request):
    return render(request, 'pages/shop/shop-6-grid.html')

def shop_list_view(request):
    return render(request, 'pages/shop/shop-list-view.html')



