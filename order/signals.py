import decimal
from accounts.models import Admin, CustomUser, Vendor
# from payment.models import Wallet, WalletHistory
from product.models import Product, ProCategory, ProductMeta, ProductVariant
from order.models import (
    Order,
    OrderBillingAddress,
    OrderPayment,
    ProductOrder,
    Cart,
    Wishlist,
    Compare,
    CartProducts,
    OrderTracking,
)

# from payment.models import Wallet
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import Group


@receiver(post_save, sender=Order)
def signal_for_single_product_order_management(sender, instance, created, **kwargs):
    if instance.orderedByCustomer.is_customer == True:
        if created:
            cart = Cart.objects.get(id=instance.orderedCart.id)
            cart_products = CartProducts.objects.filter(
                cartByCustomer=cart.cartByCustomer
            )

            for product in cart_products:
                if int(product.cartProduct.productVariantQuantity) == 0:
                    product.cartProduct.productVariantStockStatus = "Out Of Stock"

                    product.cartProduct.save(
                        update_fields=["productVariantStockStatus"]
                    )

                if int(product.cartProduct.productVariantQuantity) > 0:
                    updatedQuantity = int(
                        product.cartProduct.productVariantQuantity
                    ) - int(product.cartProductQuantity)
                    product.cartProduct.productVariantQuantity = updatedQuantity

                    # product.cartProduct.variantProduct.productSoldQuantity = product.cartProduct.variantProduct.productSoldQuantity + \
                    #     int(product.cartProductQuantity)
                    # product.cartProduct.variantProduct.save(
                    #     update_fields=['productSoldQuantity'])
                    
                    productMetaObj = ProductMeta.objects.get(product=product.cartProduct.variantProduct)
                    productMetaObj.productSoldQuantity = productMetaObj.productSoldQuantity + int(product.cartProductQuantity)
                    productMetaObj.save(
                        update_fields=['productSoldQuantity'])

                    product.cartProduct.save(update_fields=["productVariantQuantity"])

                    # new added
                    productD = (product.cartProduct.productVariantDiscount * product.cartProductQuantity)
                    product_order_total_price = (product.cartProduct.productVariantPrice * product.cartProductQuantity)
                    product_order_final_price = (product.cartProduct.productVariantFinalPrice* product.cartProductQuantity)
                    product_order_saving = (product.cartProduct.productVariantDiscountPrice* product.cartProductQuantity)
                    product_variant_order_tax = int(product.cartProduct.productVariantTax)
                    productvar = ProductVariant.objects.get(id=product.cartProduct.id)
                    product_variant_order_final_price_after_tax = int(productvar.productVariantFinalPriceAfterTax) * int(product.cartProductQuantity)
                    product_variant_order_tax_price = int(productvar.productVariantTaxPrice) * int(product.cartProductQuantity)
                    # ,productOrderTracking=
                    product_order = ProductOrder.objects.create(
                        productOrderOrderId=instance.id,
                        productOrderPaymentTransactionId=instance.orderPayment.orderPaymentTransactionId,
                        productOrderedByCustomer=instance.orderedByCustomer,
                        productOrderBillingAddress=instance.orderBillingAddress,
                        productOrderedCart=cart,
                        productOrderedProducts=product.cartProduct,
                        productOrderedProductQuantity=product.cartProductQuantity,
                        productOrderedOrNot=instance.orderedOrNot,
                        productOrderTotalPrice=product_order_total_price,
                        productOrderFinalPrice=product_order_final_price,
                        productOrderSavings=product_order_saving,
                        productVariantOrderTax=product_variant_order_tax,
                        productVariantOrderTaxPrice=product_variant_order_tax_price,
                        productVariantOrderFinalPriceAfterTax=product_variant_order_final_price_after_tax,
                    )
                    product_order.save()


@receiver(post_save, sender=Order)
def signal_for_order_Tracking(sender, instance, created, **kwargs):
    if instance.orderedByCustomer.is_customer == True:
        if created:
            cart = Cart.objects.get(id=instance.orderedCart.id)
            cart_products = CartProducts.objects.filter(
                cartByCustomer=cart.cartByCustomer
            )

            # ---------------------------------------------------------------------------------------------------------
            # vendorlist=[]
            # uniquevendorlist=[]
            # cart_product_list=[]
            # for product in cart_products:
            #     # vendorlist.append(str(product.cartProduct.variantProduct.productVendor))
            #     order_racking_instance = OrderTracking.objects.create(
            #             trackingOrderCustomer=product.cartByCustomer, trackingOrderVendor=product.cartProduct.variantProduct.productVendor)
            #     order_racking_instance.trackingOrder.add(product.cartProduct)
            #     order_racking_instance.save()
            #     tempVar=False
            #     vendorlist.append({vendor:product.cartProduct.variantProduct.productVendor,product:product})

            # print('$$$$$$$$$$$$$$$$$$$$$$$--------vendorlist---------$$$$$$$$$$$$$$$$$$$$$$$',vendorlist)

            # for vendor in vendorlist:
            #     if vendor not in uniquevendorlist:
            #         uniquevendorlist.append(vendor)
            # ---------------------------------------------------------------------------------------------------------

            # vendorlist=[]
            cart_product_list = []
            uniquevendorlist = {
                str(product.cartProduct.variantProduct.productVendor)
                for product in cart_products
            }

            for vendor in uniquevendorlist:
                products = cart_products.filter(
                    cartProduct__variantProduct__productVendor__email=vendor
                )
                cart_product_list.append(
                    cart_products.filter(
                        cartProduct__variantProduct__productVendor__email=vendor
                    )
                )

            for products in cart_product_list:
                # if len(products):
                #     order_racking_instance = OrderTracking.objects.create(
                #         trackingOrderCustomer=products.0.cartByCustomer,trackingOrderVendor=products.0.cartProduct.variantProduct.productVendor)
                #     order_racking_instance.trackingOrder.add(*products)
                #     order_racking_instance.save()
                #     order_racking_instance=OrderTracking()
                tempVar = True
                for product in products:
                    if tempVar:
                        order_racking_instance = OrderTracking.objects.create(
                            trackingOrderOrderId=instance.id,
                            trackingOrderOrderTransactionId=instance.orderTransactionId,
                            trackingOrderCustomer=product.cartByCustomer,
                            trackingOrderVendor=product.cartProduct.variantProduct.productVendor,
                        )
                        order_racking_instance.save()
                        tempVar = False

                    order_racking_instance.trackingOrder.add(product.cartProduct)
                    order_racking_instance.save()


# ----------------------------------------------------------------
@receiver(post_save, sender=Order)
def signal_for_store_transaction_id_in_payment(sender, instance, created, **kwargs):
    if instance.orderedByCustomer.is_customer == True:
        if created:
            oderPaymentInstance = OrderPayment.objects.get(orderPaymentTransactionId=instance.orderTransactionId)
            oderPaymentInstance.orderPaymentOrderId = instance.id
            oderPaymentInstance.save()


# ----------------------------------------------------------------

# ----------------------------------------------------------------


@receiver(post_save, sender=Order)
def signal_to_store_tid_oid_in_order_billing_address(
    sender, instance, created, **kwargs
):
    if instance.orderedByCustomer.is_customer == True:
        if created:
            OrderBillingInstance = OrderBillingAddress.objects.get(
                id=instance.orderBillingAddress.id
            )
            OrderBillingInstance.orderTransactionId = instance.orderTransactionId
            OrderBillingInstance.orderId = instance.id

            OrderBillingInstance.save()


# ----------------------------------------------------------------

# ----------------------------------------------------------------


@receiver(post_save, sender=Order)
def signal_for_admin_wallet_update(sender, instance, created, **kwargs):
    if instance.orderedByCustomer.is_customer == True:
        if created:
            superUser = CustomUser.objects.get(email="admin@gmail.com")
            adminInstance = Admin.objects.get(admin=superUser)
            # adminWallet=Wallet.objects.get(walletByUser=superUser)
            adminInstance.adminWalletBalance = decimal.Decimal(float(adminInstance.adminWalletBalance) + float(instance.orderPayment.orderAmount))
            
            adminInstance.save(update_fields=["adminWalletBalance"])


# ----------------------------------------------------------------


@receiver(post_save, sender=OrderTracking)
def signal_for_whole_order_status(sender, instance, **kwargs):
    # Define your condition
    orderId = instance.trackingOrderOrderId
    condition = Q(trackingOrderOrderId=orderId) & Q(trackingOrderStatus="Delivered")

    # Check if the condition is true for all objects
    status = (
        OrderTracking.objects.filter(condition).count()
        == OrderTracking.objects.filter(trackingOrderOrderId=orderId).count()
    )
    if status:
        order = Order.objects.get(id=orderId)
        order.orderedOrNot = status
        order.save(update_fields=["orderedOrNot"])
    else:
        order = Order.objects.get(id=orderId)
        order.orderedOrNot = False
        order.save(update_fields=["orderedOrNot"])


# Wallet and commission management--------------------------------
# @receiver(post_save, sender=OrderTracking)
# def signal_for_wallet_and_commission_management(sender, instance, created, **kwargs):
#     if instance.trackingOrderStatus == "Delivered":
#         superUser = CustomUser.objects.get(email="admin@gmail.com")
#         admin = Admin.objects.get(admin=superUser)
#         adminWallet = Wallet.objects.get(walletByUser=superUser)

#         productsOfProductOrder = ProductOrder.objects.filter(
#             productOrderOrderId=instance.trackingOrderOrderId
#         )

#         products = instance.trackingOrder.all()
#         for product in products:
#             productObject = ProductVariant.objects.get(id=product.id)

#             productObjectForQuantity = productsOfProductOrder.get(
#                 productOrderedProducts=productObject
#             )
#             quantity = productObjectForQuantity.productOrderedProductQuantity

#             productVendor = product.variantProduct.productVendor
#             vendor = Vendor.objects.get(vendor=productVendor)
#             vendorWallet = Wallet.objects.get(walletByUser=productVendor)

#             parentCatList = product.variantProduct.proCategory.get_all_parents()

#             # Initial value for maxCommission
#             maxCommission = product.variantProduct.proCategory.categoryProductCommission

#             for cat in parentCatList:
#                 if maxCommission < cat.categoryProductCommission:
#                     maxCommission = cat.categoryProductCommission

#             commissionAmount = decimal.Decimal((float(product.productVariantFinalPrice) * float(maxCommission)) / float(100))

#             # Managing admin user commission and walet balance in ADMIN Model
#             admin.adminCommissionProfit = decimal.Decimal(
#                 float(admin.adminCommissionProfit)
#                 + (float(commissionAmount) * float(quantity))
#             )

#             # Managing admin wallet
#             adminWallet.walletBalance = decimal.Decimal(
#                 float(adminWallet.walletBalance)
#                 + (float(commissionAmount) * float(quantity))
#             )

#             # Managing admin user walet history in WALLET HISTORY Model
#             adminWalletHistory = WalletHistory.objects.create(
#                 walletHistoryByUser=adminWallet
#             )
#             adminWalletHistory.walletHistoryCredit = float(commissionAmount) * float(
#                 quantity
#             )
#             adminWalletHistory.walletHistoryBalance = float(adminWallet.walletBalance)

#             # adminWalletHistory.walletHistoryBalance=decimal.Decimal(float(adminWallet.walletBalance) + (float(commissionAmount)*float(quantity)))
#             adminWalletHistory.walletHistoryOfOrderId = instance.trackingOrderOrderId
#             adminWalletHistory.walletHistoryOfOrderTransactionId = (
#                 instance.trackingOrderOrderTransactionId
#             )
#             adminWalletHistory.walletHistoryOfTrackingId = instance.id
#             adminWalletHistory.save()

#             admin.save(update_fields=["adminCommissionProfit"])
#             adminWallet.save(update_fields=["walletBalance"])

#             # Managing vendor user wallet balance in VENDOR Model
#             vendor.vendorWalletBalance = decimal.Decimal(
#                 float(vendor.vendorWalletBalance)
#                 + (
#                     (float(product.productVariantFinalPrice) - float(commissionAmount))
#                     * float(quantity)
#                 )
#             )

#             # Managing Vendor Wallet balance in Wallet Module
#             vendorWallet.walletBalance = decimal.Decimal(
#                 float(vendorWallet.walletBalance)
#                 + (
#                     (float(product.productVariantFinalPrice) - float(commissionAmount))
#                     * float(quantity)
#                 )
#             )

#             # Managing vendor user wallet history in WALLET HISTORY Model
#             vendorWalletHistory = WalletHistory.objects.create(
#                 walletHistoryByUser=vendorWallet
#             )
#             vendorWalletHistory.walletHistoryCredit = (
#                 float(product.productVariantFinalPrice) - float(commissionAmount)
#             ) * float(quantity)
#             vendorWalletHistory.walletHistoryBalance = float(vendorWallet.walletBalance)

#             # vendorWalletHistory.walletHistoryBalance=decimal.Decimal(float(vendorWallet.walletBalance) + ((float(product.productVariantFinalPrice) - float(commissionAmount))*float(quantity)))
#             vendorWalletHistory.walletHistoryOfOrderId = instance.trackingOrderOrderId
#             vendorWalletHistory.walletHistoryOfOrderTransactionId = (
#                 instance.trackingOrderOrderTransactionId
#             )
#             vendorWalletHistory.walletHistoryOfTrackingId = instance.id
#             vendorWalletHistory.save()

#             vendor.save(update_fields=["vendorWalletBalance"])
#             vendorWallet.save(update_fields=["walletBalance"])


# ----------------------------------------------------------------


@receiver(post_save, sender=CustomUser)
def signal_cart_creation(sender, instance, created, **kwargs):
    group = Group.objects.get(name="Customer")
    if instance.is_customer == True:
        if created:
            Cart.objects.create(cartByCustomer=instance).save()


@receiver(post_save, sender=CustomUser)
def signal_wishlist_creation(sender, instance, created, **kwargs):
    if instance.is_customer == True:
        if created:
            Wishlist.objects.create(wishlistByCustomer=instance).save()


@receiver(post_save, sender=CustomUser)
def signal_compare_product_list_creation(sender, instance, created, **kwargs):
    if instance.is_customer == True:
        if created:
            Compare.objects.create(compareByCustomer=instance).save()
