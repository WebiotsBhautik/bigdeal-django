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





# def payment_complete(request):
#     body = json.loads(request.body)
    
#     if 'addressId' in body:
#         addressId = body["addressId"]
#         strPrice = body["price"]
        
#         decimalPrice=Decimal(strPrice)
#         price=convert_amount_based_on_currency(decimalPrice,request)
#         cartid = body["cartid"]
#         orderpaymentmethodname = body["orderpaymentmethodname"]
        
#         cookie_value = request.COOKIES.get('couponCode')
#         if cookie_value:
#             couponCode=cookie_value
#         else:
#             couponCode=''

#         couponDiscountAmount=0  
#         createHistory = False
#         if couponCode:
#             try:
#                 coupon=Coupon.objects.get(couponCode=couponCode)
#                 couponUsesByCustomer=CouponHistory.objects.filter(coupon=coupon)
#                 if len(couponUsesByCustomer) < coupon.usageLimit and int(coupon.numOfCoupon) > 0:
#                     currentDateTime = timezone.now()
#                     if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
#                         if coupon.couponType == "Fixed":
#                             price=price-int(coupon.couponDiscountOrFixed)
#                         if coupon.couponType == "Percentage":
#                             couponDiscountAmount=((price*coupon.couponDiscountOrFixed)/100)
#                             price=price-couponDiscountAmount
#                         createHistory = True
#             except:
#                 pass

#         order_billing_address_instance = OrderBillingAddress.objects.get(id=addressId)
#         paymentmethod = PaymentMethod.objects.get(paymentMethodName=orderpaymentmethodname)

#         if 'rpPaymentId' in body:
#             rpPaymentId = body["rpPaymentId"]
#             order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=rpPaymentId, orderAmount=price, orderPaymentMethodName=paymentmethod,)
#             order_payment_instance.save()
#             cart = Cart.objects.get(id=cartid)
#             order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
#                                                   orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
#             order_instance.save()
            
#             if createHistory:
#                 coupon.numOfCoupon=coupon.numOfCoupon-1
#                 coupon.save()
#                 CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
#             CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
#             remove_copon= request.COOKIES.get('couponCode')
#             if remove_copon:
#                 response = HttpResponse("Currency removed")
#                 response.delete_cookie('couponCode')
#                 return response 
#             return JsonResponse(data={'message': 'Payment completed'},safe=False)

#         if 'payPalTransactionID' in body:
#             payPalTransactionID = body["payPalTransactionID"]
#             order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=payPalTransactionID, orderAmount=price, orderPaymentMethodName=paymentmethod,)
#             order_payment_instance.save()
#             cart = Cart.objects.get(id=cartid)
#             order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
#                                                   orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
#             order_instance.save()
            
#             if createHistory:
#                 coupon.numOfCoupon=coupon.numOfCoupon-1
#                 coupon.save()
#                 CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
#             CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
#             remove_copon= request.COOKIES.get('couponCode')
#             if remove_copon:
#                 response = HttpResponse("Currency removed")
#                 response.delete_cookie('couponCode')
#                 return response 
#             return JsonResponse(data={'message': 'Payment completed'},safe=False)
#     else:
#         strPrice = body["price"]
#         decimalPrice=Decimal(strPrice)
#         price=convert_amount_based_on_currency(decimalPrice,request)
#         fname = body["fname"]
#         lname = body["lname"]
#         uname = body["uname"]
#         email = body["email"]
#         address1 = body["address1"]
#         address2 = body["address2"]
#         country = body["country"]
#         city = body["city"]
#         zip = body["zip"]
#         cartid = body["cartid"]
#         orderpaymentmethodname = body["orderpaymentmethodname"]
        
#         cookie_value = request.COOKIES.get('couponCode')
#         if cookie_value:
#             couponCode=cookie_value
#         else:
#             couponCode=''
        
#         couponDiscountAmount=0
#         createHistory = False
#         if couponCode:
#             try:
#                 coupon=Coupon.objects.get(couponCode=couponCode)
#                 couponUsesByCustomer=CouponHistory.objects.filter(coupon=coupon)
#                 if len(couponUsesByCustomer) < coupon.usageLimit and int(coupon.numOfCoupon) > 0:
#                     currentDateTime = timezone.now()
#                     if coupon.expirationDateTime >= currentDateTime and price >= coupon.minAmount:
#                         if coupon.couponType == "Fixed":
#                             price=price-int(coupon.couponDiscountOrFixed)
#                         if coupon.couponType == "Percentage":
#                             couponDiscountAmount=((price*coupon.couponDiscountOrFixed)/100)
#                             price=price-couponDiscountAmount
#                         createHistory = True
#             except:
#                 pass     
            
#         order_billing_address_instance = OrderBillingAddress.objects.create(customer=request.user, customerFirstName=fname, customerLastName=lname, customerUsername=uname,
#                                                                             customerEmail=email, customerAddress1=address1, customerAddress2=address2, customerCountry=country, customerCity=city, customerZip=zip)
#         order_billing_address_instance.save()
#         paymentmethod = PaymentMethod.objects.get(paymentMethodName=orderpaymentmethodname)

#         if 'rpPaymentId' in body:
#             rpPaymentId = body["rpPaymentId"]
#             order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user, orderPaymentTransactionId=rpPaymentId, orderAmount=price, orderPaymentMethodName=paymentmethod)
#             order_payment_instance.save()
#             cart = Cart.objects.get(id=cartid)
#             order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
#                                                   orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
#             order_instance.save()
            
            
#             if createHistory:
#                 coupon.numOfCoupon=coupon.numOfCoupon-1
#                 coupon.save()
#                 CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
#             CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
#             remove_copon= request.COOKIES.get('couponCode')
#             if remove_copon:
#                 response = HttpResponse("Currency removed")
#                 response.delete_cookie('couponCode')
#                 return response 
#             return JsonResponse(data={'message': 'Payment completed'},safe=False)

#         if 'payPalTransactionID' in body:
#             payPalTransactionID = body["payPalTransactionID"]
#             order_payment_instance = OrderPayment.objects.create(orderPaymentFromCustomer=request.user,
#                                                                  orderPaymentTransactionId=payPalTransactionID,
#                                                                  orderAmount=price, orderPaymentMethodName=paymentmethod)
#             order_payment_instance.save()
#             cart = Cart.objects.get(id=cartid)
#             order_instance = Order.objects.create(orderedByCustomer=request.user, orderTransactionId=order_payment_instance.orderPaymentTransactionId, orderBillingAddress=order_billing_address_instance,
#                                                   orderedCart=cart, orderPayment=order_payment_instance, orderTotalPrice=cart.getFinalPriceAfterTax, orderTotalTax=cart.getTotalTax, orderSavings=cart.getTotalDiscountAmount)
#             order_instance.save()
#             if createHistory:   
#                 coupon.numOfCoupon=coupon.numOfCoupon-1
#                 coupon.save()
#                 CouponHistory.objects.create(coupon=coupon,couponHistoryByUser=order_instance.orderedByCustomer,couponHistoryByOrder=order_instance)
#             CartProducts.objects.filter(cartByCustomer=cart.cartByCustomer).delete()
#             remove_copon= request.COOKIES.get('couponCode')
#             if remove_copon:
#                 response = HttpResponse("Currency removed")
#                 response.delete_cookie('couponCode')
#                 return response 
#             return JsonResponse(data={'message': 'Payment completed'},safe=False)
  
  
  