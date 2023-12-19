from django.urls import path
from .import views

urlpatterns = [
    
# AUTHNTICATION ROUTES
    
    path('setCookie',views.setCookie, name='setCookie'),
    path('set_currency_to_session',views.set_currency_to_session,name='set_currency_to_session'),
    path('get_selected_currency',views.get_selected_currency,name='get_selected_currency'),
    path('add_cookie_currency',views.add_cookie_currency,name='add_cookie_currency'),



    path('', views.index, name='index'),
    path('signup_page', views.signup_page, name='signup_page'),
    path('login_page', views.login_page, name='login_page'),
    path('logout_page', views.logout_page, name='logout_page'),
    
    
# Forgot password routes

    path('forgot_password',views.forgot_password, name='forgot_password'),
    path('verify_token',views.verify_token, name='verify_token'),
    path('update_password',views.update_password, name='update_password'),
    path('change_password',views.change_password,name='change_password'),
    
    path('contact_us',views.contact_us,name='contact_us'),
    

    
    
# HOME PAGES ROUTES

    path('index',views.index,name='index'),
    path('layout2',views.layout2,name='layout2'),
    path('layout3',views.layout3,name='layout3'),
    path('layout4',views.layout4,name='layout4'),
    path('layout5',views.layout5,name='layout5'),
    path('electronics',views.electronics,name='electronics'),
    path('vegetable',views.vegetable,name='vegetable'),
    path('furniture',views.furniture,name='furniture'),
    path('cosmetic',views.cosmetic,name='cosmetic'),
    path('kids',views.kids,name='kids'),
    path('tools',views.tools,name='tools'),
    path('grocery',views.grocery,name='grocery'),
    path('pets',views.pets,name='pets'),
    path('farming',views.farming,name='farming'),
    path('digital_marketplace',views.digital_marketplace,name='digital_marketplace'),
    
    
    
    
    
# SHOP PAGES ROUTES

    path('create_query_params_url/<str:path>', views.create_query_params_url, name='create_query_params_url'),
    
    path('search_query_params_url', views.search_query_params_url, name='search_query_params_url'),
    
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
    
    
    
    
    path('customer_review',views.customer_review, name='customer_review'),
    
# PRODUCT PAGES ROUTES


    path('get_product_variant',views.get_product_variant,name='get_product_variant'),
    
    path('product-detail/<str:id>', views.left_slidebar, name='left_slidebar'),
    
    path('quick_view',views.quick_view,name='quick_view'),

    # path('product-detail/<slug:brand_slug>', views.left_slidebar, name='left_slidebar_with_brands'),

    # path('shop-left-sidebar/<slug:brand_slug>', views.products_by_brand, name='products_by_brand'),
    
    # path('shop-left-sidebar/<str:brand_id>', views.left_slidebar_with_brands, name='left_slidebar_with_brands'),
    

    path('right_sidebar/<str:id>', views.right_sidebar, name='right_sidebar'),
    path('no_sidebar/<str:id>', views.no_sidebar, name='no_sidebar'),
    path('bundle/<str:id>', views.bundle, name='bundle'),
    path('image_swatch/<str:id>', views.image_swatch, name='image_swatch'),
    path('vertical_tab/<str:id>', views.vertical_tab, name='vertical_tab'),
    path('video_thumbnail/<str:id>', views.video_thumbnail, name='video_thumbnail'),
    path('image_4/<str:id>', views.image_4, name='image_4'),
    path('sticky/<str:id>', views.sticky, name='sticky'),
    path('accordian/<str:id>', views.accordian, name='accordian'),
    path('product_360_view/<str:id>', views.product_360_view, name='product_360_view'),
    path('left_image/<str:id>', views.left_image, name='left_image'),
    path('right_image/<str:id>', views.right_image, name='right_image'),
    path('image_outside/<str:id>', views.image_outside, name='image_outside'),
    path('thumbnail_left/<str:id>', views.thumbnail_left, name='thumbnail_left'),
    path('thumbnail_right/<str:id>', views.thumbnail_right, name='thumbnail_right'),
    path('thumbnail_bottom/<str:id>', views.thumbnail_bottom, name='thumbnail_bottom'),
    path('element_productbox', views.element_productbox, name='element_productbox'),
    path('element_product_slider', views.element_product_slider, name='element_product_slider'),
    path('element_no_slider', views.element_no_slider, name='element_no_slider'),
    
    
    
# Pages Section Routes

    path('add_to_cart/<str:id>/<str:quantity>', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart_product_quantity_management/<str:id>/<str:actionType>', views.add_to_cart_product_quantity_management, name='add_to_cart_product_quantity_management'),

    

    path('search_bar/',views.search_bar, name='search_bar'),
    path('search_bar/<str:params>',views.search_bar, name='search_bar_with_params'),
    path('search_products/', views.search_products, name='search_products'),
    
    
    path('compare_page',views.compare_page, name='compare_page'),
    path('compare_page2',views.compare_page2, name='compare_page2'),
    path('compare_products/<str:id>',views.compare_products,name='compare_products'),
    path('delete_compare_product/<str:id>',views.delete_compare_product, name='delete_compare_product'),
    
    
    path('user_authenticate',views.user_authenticate, name='user_authenticate'),
    
    path('page_not_found',views.page_not_found, name='page_not_found'),
    path('faq_page',views.faq_page, name='faq_page'),
    path('coming_soon',views.coming_soon, name='coming_soon'),
    path('about_page',views.about_page, name='about_page'),
    path('review',views.review, name='review'),
    path('typography',views.typography, name='typography'),
    path('look_book',views.look_book, name='look_book'),
    path('collection',views.collection, name='collection'),
    
    # User dashboard routes
    path('user_dashboard',views.user_dashboard,name='user_dashboard'),
    path('add_address',views.add_address, name="add_address"),
    path('get_address',views.get_address, name='get_address'),
    path('save_address',views.save_address,name='save_address'),
    path('remove_address/<str:id>',views.remove_address, name='remove_address'),
    path('profile',views.profile,name='profile'),
    
    
    # Wishlist routes
    path('add_to_wishlist/<str:id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist_page',views.wishlist_page,name='wishlist_page'),
    path('delete_wishlist_product/<str:id>',views.delete_wishlist_product, name='delete_wishlist_product'),
    path('add_to_cart_from_wishlist/<str:id>/<str:quantity>',views.add_to_cart_from_wishlist,name='add_to_cart_from_wishlist'),

    
    # Cart page
    path('add_to_cart/<str:id>/<str:quantity>', views.add_to_cart, name='add_to_cart'),
    path('cart_page', views.cart_page, name='cart_page'),
    path('delete_cart_product/<str:id>',views.delete_cart_product, name='delete_cart_product'),
    # path('delete_cart_product_form_header_button/<str:id>',views.delete_cart_product_form_header_button,name='delete_cart_product_form_header_button'),
    # path('delete_cart_all_product', views.delete_cart_all_product,name='delete_cart_all_product'),
    
    
    # Checkout Page Routes
    path('cart_to_checkout_validation',views.cart_to_checkout_validation,name='cart_to_checkout_validation'),
    path('validate_coupon/', views.validate_coupon, name='validate_coupon'),
    path('checkout_page',views.checkout_page,name='checkout_page'),
    path('checkout_2_page',views.checkout_2_page,name='checkout_2_page'),

    

    
# Blog Pages Routes

    path('blog_details/<str:id>',views.blog_details, name='blog_details'),
    path('add_comment/<str:id>',views.add_comment, name='add_comment'),
    
    
    path('blog_left_sidebar',views.blog_left_sidebar, name='blog_left_sidebar'),
    # path('left_sidebar_for_selected_category/<str:id>',views.left_sidebar_for_selected_category, name='left_sidebar_for_selected_category'),
    path('blog_right_sidebar',views.blog_right_sidebar, name='blog_right_sidebar'),
    path('blog_no_sidebar',views.blog_no_sidebar,name='blog_no_sidebar'),
    path('blog_creative_left_sidebar',views.blog_creative_left_sidebar,name='blog_creative_left_sidebar')


]







