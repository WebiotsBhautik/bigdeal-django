from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse



# Create your views here.


# HOME PAGES SECTION 

def index(request):
    return render(request,'pages/home/ms1/index.html')

def layout2(request):
    return render(request, 'pages/home/ms2/layout-2.html')

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
    return render(request, 'pages/home/digital marketplace/digital-marketplace.html')


