# @csrf_exempt
# def add_to_cart_product_quantity_management(request, id, actionType):
#     if request.user.is_authenticated:
#         productVariant = ProductVariant.objects.get(id=id)
#         cart = Cart.objects.get(cartByCustomer=request.user)

#         if CartProducts.objects.filter(cartByCustomer=request.user, cartProduct=productVariant).exists():
#             cartProductObject = CartProducts.objects.get(cartByCustomer=request.user, cartProduct=productVariant)

#             if actionType == "plus":
#                 if productVariant.productVariantQuantity > 0:
#                     cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + 1
#                     cartProductObject.save()
#                     cartTotalPrice = cart.getTotalPrice
#                     cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
#                     data = {
#                         "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
#                         "cartTotalPrice": cartTotalPrice,
#                         "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
#                         "taxPrice":cart.getTotalTax
#                     }
#                     return JsonResponse(data, safe=False)
#                 else:
#                     # cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity + 1
#                     # cartProductObject.save() 
#                     cartTotalPrice = cart.getTotalPrice
#                     cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
#                     data = {
#                         "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
#                         "cartTotalPrice": cartTotalPrice,
#                         "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
#                         "taxPrice":cart.getTotalTax
#                     }
#                     return JsonResponse(data, safe=False)

#             if actionType == "minus":
#                 cartProductObject.cartProductQuantity = cartProductObject.cartProductQuantity - 1
#                 cartProductObject.save()
#                 cartTotalPrice = cart.getTotalPrice
#                 cartTotalPriceAfterTax = cart.getFinalPriceAfterTax
#                 data = {
#                     "quantityTotalPrice": cartProductObject.cartProductQuantityTotalPrice,
#                     "cartTotalPrice": cartTotalPrice,
#                     "cartTotalPriceAfterTax": cartTotalPriceAfterTax,
#                     "taxPrice":cart.getTotalTax
#                 }
#                 return JsonResponse(data, safe=False)
            
#     else:
#         productVariant = ProductVariant.objects.get(id=id)
#         product_id = productVariant.variantProduct.id
#         get_Item = request.COOKIES.get('cart').replace("\'", "\"") if request.COOKIES.get('cart') is not None else None

#         if (get_Item is not None and get_Item != "null"):
#             cart_products = json.loads(get_Item)
#         else:
#             cart_products = []

#         if actionType == "plus" and cart_products:
#             print("in plus")

#             for item in cart_products:
#                 if str(id) == item['variant_id'] and str(product_id) == item['product_id']:
#                     item['quantity'] = int(item['quantity']) + 1
#                     item['totalPrice'] = format(item['quantity'] * item['price'],".2f")

#         if actionType == "minus" and cart_products:
#             print("in minus")
#             for item in cart_products:
#                 if str(id) == item['variant_id'] and str(product_id) == item['product_id']:
#                     if item['quantity'] >= 1:
#                         item['quantity'] -= 1
#                         item['totalPrice'] = format(item['quantity'] * item['price'],".2f")
#                     else:
#                         cart_products = [item for item in cart_products if item.get('product_id') != id]
#                         break
#         res_data = [item for item in cart_products if str(id) == item.get('variant_id') and str(product_id) == item.get('product_id')]
#         TotalPrice = sum([float(i['totalPrice']) for i in cart_products])
#         TotalTax,TotalTaxPrice,TotalFinalPriceAfterTax = get_total_tax_values(cart_products)
        
#         data = {
#                     "quantityTotalPrice": res_data[0]['totalPrice'],
#                     "cartTotalPrice": TotalPrice,
#                     "cartTotalPriceAfterTax": TotalFinalPriceAfterTax,
#                     "taxPrice":TotalTaxPrice,
#                 }

#         response = JsonResponse(data,safe=False)
#         response.set_cookie('cart', cart_products)
#         return response




# @login_required(login_url='login_page')
# def cart_to_checkout_validation(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             body = json.loads(request.body)
#             cartId = body["cartId"]
#             cart = Cart.objects.get(id=cartId)
#             cartProducts = CartProducts.objects.filter(cart=cart)
#             productList = []
#             flag = False
#             for product in cartProducts:
#                 dbProduct=ProductVariant.objects.get(id=product.cartProduct.id)
#                 if product.cartProductQuantity <= dbProduct.productVariantQuantity:
#                     pass
#                 else:
#                     productList.append({"productName":str(product.cartProduct.variantProduct.productName),"outOfStockProducts":str(product.cartProduct.productVariantQuantity)})
#             if len(productList) > 0:
#                 flag=True
            
#             if flag:
#                 data={"outOfStockProducts":productList,"flag":str(flag),}
#                 response = JsonResponse(data,safe=False)
#                 expiry_time = datetime.utcnow() + timedelta(seconds=30)
#                 response.set_cookie('checkout', 'False',expires=expiry_time)
#                 return response
#             else:
#                 data={"outOfStockProducts":productList,"flag":str(flag),}
#                 response = JsonResponse(data,safe=False)
#                 expiry_time = datetime.utcnow() + timedelta(seconds=30)
#                 response.set_cookie('checkout', 'True',expires=expiry_time)
#                 return response
#     else:
#         return redirect('login_page')






# def add_address(request):
#     body = json.loads(request.body)
#     fname = body["fname"]
#     lname = body["lname"]
#     username = body["username"]
#     email = body["email"]
#     mobno = body["mobno"]
#     address1 = body["address1"]
#     address2 = body["address2"]
#     country = body["country"]
#     city = body["city"]
#     zipcode = body["zipcode"]
#     customer = CustomUser.objects.get(id=request.user.id)
#     user = OrderBillingAddress.objects.create(customer=customer,customerFirstName=fname,customerLastName=lname,customerUsername=username,customerEmail=email,customerMobile=mobno,customerAddress1=address1,customerAddress2=address2,customerCountry=country,customerCity=city,customerZip=zipcode)
#     user.save()
#     return HttpResponse(request, status=200)





# def remove_address(request, id):
#     address = OrderBillingAddress.objects.get(id=id, customer=request.user)
   
#     product_orders = ProductOrder.objects.filter(productOrderedByCustomer__username=address)
   
    
#     associated_orders = Order.objects.filter(orderBillingAddress=address)
#     if associated_orders:
#         for order in associated_orders:
#             if order.orderedOrNot == True:
#                 address.delete()
#                 messages.success(request,'Address Removed Successfully')
#                 return redirect('user_dashboard')
#             else:    
#                 messages.warning(request,'Address cannot be removed as it is associated with a delivered order')
#                 return redirect('user_dashboard')
#         else:
#             address.delete()
#             messages.success(request,'Address Removed Successfully')
#             return redirect('user_dashboard')
#     else:
#         address.delete()
#         messages.success(request,'Address Removed Successfully')
#         return redirect('user_dashboard')
    


# def get_address(request):
#      if request.method == 'POST':
#         body = json.loads(request.body)
#         addressId = body['addressId']
#         address=OrderBillingAddress.objects.get(id=addressId)
#         data = {'fname': address.customerFirstName, 'lname': address.customerLastName, 'username': address.customerUsername, 'email': address.customerEmail, 'mobno': address.customerMobile,
#         'address1': address.customerAddress1, 'address2': address.customerAddress2, 'country': address.customerCountry, 'city': address.customerCity, 'zipcode': address.customerZip}
#         return JsonResponse(data, safe=False)



        

        
# @login_required(login_url='login_page')
# def checkout_page(request):
#     customer_cart = Cart.objects.get(cartByCustomer=request.user.id)
#     cart_products = CartProducts.objects.filter(cartByCustomer=request.user.id)
#     cart_products_demo = serializers.serialize("json", CartProducts.objects.filter(cartByCustomer=request.user.id))
#     totalCartProducts = cart_products.count()

#     customer_wishlist = Wishlist.objects.get(wishlistByCustomer=request.user.id)
#     wishlist_products = customer_wishlist.wishlistProducts.all()
#     totalWishlistProducts = wishlist_products.count()
    
    

#     getTotalTax = customer_cart.getTotalTax
#     getTotalPrice = customer_cart.getTotalPrice

#     customer = CustomUser.objects.get(id=request.user.id)
#     billingAddresses = OrderBillingAddress.objects.filter(customer=customer)
    
    
#     cookie_value = request.COOKIES.get('couponCode')
#     couponAmount = 0
#     if cookie_value:
#         coupon = Coupon.objects.filter(couponCode=cookie_value)
#         couponObj=coupon.first()
        
#         if len(coupon) == 1:
#             couponUsesByCustomer=CouponHistory.objects.filter(coupon=couponObj)
#             if len(couponUsesByCustomer) < couponObj.usageLimit and int(couponObj.numOfCoupon) > 0:
#                 currentDateTime = timezone.now()
#                 if couponObj.expirationDateTime >= currentDateTime and getTotalPrice >= couponObj.minAmount:
#                     if couponObj.couponType == "Fixed":
#                         couponAmount=int(couponObj.couponDiscountOrFixed)
#                     if couponObj.couponType == "Percentage":
#                         couponDiscountAmount=((getTotalPrice*couponObj.couponDiscountOrFixed)/100)
#                         couponAmount=couponDiscountAmount
#     else:
#         pass
        
#     currency = get_currency_instance(request)
#     currency_code = currency.code
#     getTotalPriceForRazorPay = (decimal.Decimal(float(getTotalPrice))) * currency.factor * 100
#     couponAmountForRazorPay = (decimal.Decimal(float(couponAmount))) * currency.factor * 100
#     getTotalTaxForRazorPay = (decimal.Decimal(float(getTotalTax))) * currency.factor * 100
    
#     finalAmountForRazorPay=(getTotalPriceForRazorPay-couponAmountForRazorPay)+getTotalTaxForRazorPay
#     payment = client.order.create({'amount': int(finalAmountForRazorPay), 'currency': currency_code, 'payment_capture': 1})
#     finalAmount=(getTotalPrice-couponAmount)+getTotalTax
    
#     active_banner_themes = BannerTheme.objects.filter(is_active=True)

    
#     context = {"breadcrumb": {"parent": "Checkout", "child": "Checkout"},
#                "Cart": customer_cart, "cart_products": cart_products, "totalCartProducts": totalCartProducts,
#                "wishlist": customer_wishlist, "wishlist_products": wishlist_products, "totalWishlistProducts": totalWishlistProducts,
#                "cart_products_demo": cart_products_demo,
#                "getTotalTax": getTotalTax,
#                "getFinalPriceAfterTax": finalAmount,
               
#                "getTotalPrice": getTotalPrice,
#                "couponAmount":couponAmount,
#                "billingAddresses": billingAddresses,
#                "payment": payment,
#                "rsk": settings.RAZORPAY_KEY_ID,
#                "ppl":settings.PAYPAL_CLIENT_ID,
#                 'active_banner_themes':active_banner_themes,
#                }
        
#     return render(request, 'pages/pages/checkout.html', context)







