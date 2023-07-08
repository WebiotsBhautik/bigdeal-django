from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from accounts.models import CustomUser
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import auth
from .models import Banner,BannerTheme,BannerType
from product.models import (AttributeName, MultipleImages, ProBrand, ProCategory, Product,
                            ProductAttributes, ProductReview, ProductVariant,AttributeValue,ProductMeta)





# Create your views here.


def setCookie(request):
    response = HttpResponse('Cookie Set')
    response.set_cookie('login_status', True)
    return response

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
    return render(request,'pages/home/ms1/index.html')

def layout2(request):
    banners = Banner.objects.filter(bannerTheme__bannerThemeName='Megastore2 Demo')
    brands = ProBrand.objects.all()
    layout2_category = ProCategory.objects.get(categoryName='ms2')
    subcategories = layout2_category.get_descendants(include_self=True)
    layout2_products = Product.objects.filter(proCategory__in=subcategories)
    
    products_by_subcategory = {}
    
     # Retrieve products for each subcategory
    for subcategory in subcategories:
        products = Product.objects.filter(proCategory=subcategory)
        products_by_subcategory[subcategory] = products

    
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Default"},
               'allbanners':banners,
               'allbrands':brands,
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


