# def order_success(request): 
#     if request.user.is_authenticated:
#         customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
#         cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
#         totalCartProducts = cart_products.count()   
        
#         customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
#         wishlist_products = customer_wishlist.wishlistProducts.all()
#         totalWishlistProducts = wishlist_products.count()
    
#         customer = Customer.objects.get(customer=request.user)
    
        
#         order = Order.objects.filter(orderedByCustomer=request.user.id).order_by('-orderCreatedAt').first()
    
#         if order is not None:
#             paymentmethod = order.orderPayment.orderPaymentMethodName
#             products = ProductOrder.objects.filter(productOrderOrderId=order.id)
#         else:
#             paymentmethod = None
#             products = []
#     else:
#         return redirect('login_page')
    
#     active_banner_themes = BannerTheme.objects.filter(is_active=True)

    
#     context = {
#         "breadcrumb": {"parent": "Order-Success", "child": "child"},
#         "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
#         "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
#         "orderid": order.id if order else None,
#         "transactionId": order.orderPayment.orderPaymentTransactionId if order else None,
#         "orderdate": order.orderCreatedAt if order else None,
#         "orderprice": order.orderTotalPrice if order else None,
#         "orderTax": order.orderTotalTax if order else None,
#         "ordersubtotal": order.orderPrice if order else None,
#         "products": products if order else None,
#         "orderaddress": order.orderBillingAddress if order else None,
#         "contactno": customer.customerContact,
#         "paymentmethod": paymentmethod if order else None,
#         'active_banner_themes':active_banner_themes,

#     }
#     return render(request, 'pages/pages/order-success.html', context)




# def order_tracking(request, id):
#     customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
#     cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
#     totalCartProducts = cart_products.count()

#     customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
#     wishlist_products = customer_wishlist.wishlistProducts.all()
#     totalWishlistProducts = wishlist_products.count()

#     productOrders = OrderTracking.objects.filter(
#         trackingOrderCustomer=request.user, trackingOrderOrderId=id)
    
#     active_banner_themes = BannerTheme.objects.filter(is_active=True)


#     context = {"breadcrumb": {"parent": "Order Tracking", "child": "Order tracking"},
#                "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
#                "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
#                "productOrders": productOrders,
#                 'active_banner_themes':active_banner_themes,
#                }
#     return render(request, 'pages/pages/order-tracking.html', context)