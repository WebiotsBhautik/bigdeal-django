from django.urls import path
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    path('layout2',views.layout2,name='layout2'),
    path('layout3',views.layout3,name='layout3'),
    path('layout4',views.layout4,name='layout4'),
    path('megastore',views.megastore,name='megastore'),
    path('layout5',views.layout5,name='layout5'),
    path('layout6',views.layout6,name='layout6'),
    path('furniture',views.furniture,name='furniture'),
    path('cosmetic',views.cosmetic,name='cosmetic'),
    path('kids',views.kids,name='kids'),
    path('tools',views.tools,name='tools'),
    path('grocery',views.grocery,name='grocery'),
    path('pets',views.pets,name='pets'),
    path('farming',views.farming,name='farming'),
    path('digital_marketplace',views.digital_marketplace,name='digital_marketplace'),
    
    
    
    
    
# Shop pages routes
    
    path('shop_left_sidebar', views.shop_left_sidebar, name='shop_left_sidebar'),
    path('shop_right_sidebar', views.shop_right_sidebar, name='shop_right_sidebar'),
    path('shop_no_sidebar', views.shop_no_sidebar, name='shop_no_sidebar'),
    path('shop_sidebar_popup', views.shop_sidebar_popup, name='shop_sidebar_popup'),
    path('shop_metro', views.shop_metro, name='shop_metro'),
    path('shop_full_width', views.shop_full_width, name='shop_full_width'),
    path('shop_infinite_scroll', views.shop_infinite_scroll, name='shop_infinite_scroll'),
    path('shop_3grid', views.shop_3grid, name='shop_3grid'),
    path('shop_6grid', views.shop_6grid, name='shop_6grid'),
    path('shop_list_view', views.shop_list_view, name='shop_list_view'),

]
