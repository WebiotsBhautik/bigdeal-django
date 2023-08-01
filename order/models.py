import uuid
from django.db import models
from accounts.models import CustomUser
from product.models import ProductVariant
from django.utils.text import slugify
from accounts.get_username import get_request
import random
from string import digits, ascii_uppercase
from django.core.validators import RegexValidator

# Create your models here.



class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cartByCustomer = models.OneToOneField(CustomUser, on_delete=models.CASCADE,verbose_name='Customer')
    cartTotalPrice = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='Total Price')
    cartOrdered = models.BooleanField(
        default=False, verbose_name='Cart Ordered')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.cartByCustomer)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Cart, self).save(*args, **kwargs)

    def getCartProducts(self):
        return " | ".join([str(cp) for cp in self.cartProducts.all()])

    @property
    def cartTotalProduct(self):
        totalCartProduct = CartProducts.objects.filter(cartByCustomer=self.cartByCustomer).count()
        return totalCartProduct
    
    @property
    def getTotalPrice(self):
        price = 0
        products = CartProducts.objects.filter(
            cartByCustomer=self.cartByCustomer)
        for p in products:
            price += int(p.cartProductQuantityTotalPrice)
        return price
    
    @property
    def getFinalPriceAfterTax(self):
        price = 0.00
        products = CartProducts.objects.filter(
            cartByCustomer=self.cartByCustomer)
        for p in products:
            amount=p.cartProductQuantityFinalPrice
            price += int(amount)
        return price
    
    @property
    def getTotalTax(self):
        amount = 0
        products = CartProducts.objects.filter(
            cartByCustomer=self.cartByCustomer)
        for p in products:
            amount += int(p.cartProductQuantityTotalTax)
        return amount
    
    @property
    def getTotalDiscountAmount(self):
        amount = 0
        products = CartProducts.objects.filter(
            cartByCustomer=self.cartByCustomer)
        for p in products:
            amount += int(p.cartProductQuantityTotalDiscountAmount)
        return amount
    
    
    
class CartProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True,null=True, verbose_name='Cart')
    cartByCustomer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Customer')
    cartProduct = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Product')
    cartProductQuantity = models.PositiveIntegerField(verbose_name='Quantity')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.cartProduct)
    
    @property
    def cartProductQuantityTotalPrice(self):
        totalQuantityFinalPrice= int(self.cartProductQuantity) * int(self.cartProduct.productVariantFinalPrice)
        return totalQuantityFinalPrice
    
    @property
    def cartProductQuantityFinalPrice(self):
        totalQuantityFinalPriceAfterTax= int(self.cartProductQuantity) * int(self.cartProduct.productVariantFinalPriceAfterTax)
        return totalQuantityFinalPriceAfterTax


    @property
    def cartProductQuantityTotalTax(self):
        quantityTotalTax= int(self.cartProductQuantity) * int(self.cartProduct.productVariantTaxPrice)
        return quantityTotalTax
    
    @property
    def cartProductQuantityTotalDiscountAmount(self):
        totalDiscountAmount= int(self.cartProductQuantity) * int(self.cartProduct.productVariantDiscountPrice)
        return totalDiscountAmount



    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        req = get_request().user
        self.cartByCustomer = req
        super(CartProducts, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Cart Product'
        verbose_name_plural = 'Cart Products'



class OrderBillingAddress(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    customerFirstName = models.CharField(max_length=200,verbose_name='First Name')
    customerLastName = models.CharField(max_length=200,verbose_name='Last Name')
    customerUsername = models.CharField(max_length=200, null=True, blank=True,verbose_name='Username')
    customerEmail = models.EmailField(max_length=255,verbose_name='Email')
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    customerMobile=models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = False,blank=True,null=True,verbose_name='Contact')
    customerAddress1 = models.TextField(verbose_name='Address')
    customerAddress2 = models.TextField(default='Home',verbose_name='Sub Address')
    customerCountry = models.CharField(max_length=200,verbose_name='Country')
    customerCity = models.CharField(max_length=200,verbose_name='City')
    customerZip = models.CharField(max_length=200,verbose_name='Zip')

    orderTransactionId=models.CharField(max_length = 255,blank=True,null=True,verbose_name='Transaction Id')
    orderId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Order ID')

    orderBillingAddressCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    orderBillingAddressModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')

    def __str__(self):
        return self.customerUsername
    
    def get_full_name(self):
        return self.customerFirstName+" "+self.customerLastName
    get_full_name.short_description = 'Name'

    class Meta:
        verbose_name = 'Billing Address'
        verbose_name_plural = 'Billing Address'
        
        
class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paymentMethodName=models.CharField(max_length=255,verbose_name='Method Name')
    paymentMethodCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    paymentMethodModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.paymentMethodName)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(PaymentMethod, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Payment Method'
        
        
class OrderPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orderPaymentFromCustomer=models.ForeignKey(CustomUser,on_delete=models.CASCADE,verbose_name='Customer',related_name='opfc')
    orderAmount=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Amount')
    orderPaymentMethodName=models.ForeignKey(PaymentMethod,on_delete=models.CASCADE,verbose_name='Payment Method')
    orderPaymentTransactionId=models.CharField(max_length = 255,unique=True,verbose_name='Transaction Id')
    orderPaymentOrderId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Order ID')
    orderPaymentStatus = models.BooleanField(default=False,verbose_name='Status')
    orderPaymentCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    orderPaymentModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.orderPaymentFromCustomer)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(OrderPayment, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Payment'
        
        
        
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,verbose_name='Order ID')
    orderCreatedAt = models.DateTimeField(auto_now_add=True)
    orderModifiedAt = models.DateTimeField(auto_now=True)
    orderedByCustomer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Customer', related_name='obc')
    orderTransactionId=models.CharField(max_length = 255,blank=True,null=True,verbose_name='Transaction Id')
    orderBillingAddress=models.ForeignKey(OrderBillingAddress,on_delete=models.SET_NULL,null=True)
    orderedCart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    orderPayment=models.ForeignKey(OrderPayment,on_delete=models.CASCADE,blank=True)
    orderedOrNot = models.BooleanField(default=False,verbose_name='Status')
    orderDiscount = models.PositiveBigIntegerField(default=0, verbose_name='Discount (%)')
    orderTotalPrice = models.PositiveBigIntegerField(default=0, verbose_name='Price After Tax')
    orderPrice = models.PositiveBigIntegerField(default=0, verbose_name='Price Before Tax')
    orderSavings = models.PositiveBigIntegerField(default=0, verbose_name='Saving (Rs.)')
    orderTotalTax = models.PositiveBigIntegerField(default=0, verbose_name='Order Tax')
    orderOfferDiscount = models.PositiveBigIntegerField(default=0, verbose_name='Offer Dis Amount')
    slug = models.SlugField(unique=True, blank=True)

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i+1]))
        return slugs

    def save(self, *args, **kwargs):
        # if self.orderedOrNot == False:
        #     raise Exception("Something went wrong")

        self.orderPrice=self.orderTotalPrice-self.orderTotalTax

        self.slug = slugify(self.id)
        req = get_request().user
        self.orderedByCustomer = req
        # vendorofproduct = Product.objects.get(id=self.orderedProducts.id)
        # self.orderedProductsvendor = vendorofproduct.productVendor
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.orderedByCustomer)

    class Meta:
        verbose_name = 'Order'


class OrderTracking(models.Model):
    status = [('Order Processing', 'Order Processing'), ('Pre-Production', 'Pre-Production'),
              ('In Production', 'In Production'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trackingOrderOrderId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Order ID')
    trackingOrderOrderTransactionId=models.CharField(max_length = 255,blank=True,null=True,verbose_name='Transaction Id')
    trackingOrder = models.ManyToManyField(ProductVariant, blank=True, verbose_name='Product', related_name='tracking_orders')
    trackingOrderCustomer=models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,verbose_name='Customer',related_name='toc')
    trackingOrderVendor=models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,verbose_name='Vendor',related_name='tov')
    trackingOrderStatus = models.CharField(max_length=255, choices=status, verbose_name='Status', blank=True, null=True, default='Order Processing')

    trackingCreatedAt = models.DateTimeField(auto_now_add=True)
    trackingModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated at')
    class Meta:
        verbose_name = 'Tracking'

    def getProducts(self):
        return " , ".join([str(cp) for cp in self.trackingOrder.all()])

    getProducts.short_description = "Products"

class ProductOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productOrderCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    productOrderModifiedAt = models.DateTimeField(auto_now=True)
    productOrderOrderId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Order ID')
    productOrderPaymentTransactionId=models.CharField(max_length = 255,blank=True, null=True,verbose_name='Transaction Id')
    productOrderTrackingId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Tracking ID')
    productOrderedByCustomer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Customer', related_name='pobc')
    productOrderBillingAddress=models.ForeignKey(OrderBillingAddress,on_delete=models.SET_NULL,null=True)     
    productOrderedCart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    productOrderedProducts = models.ForeignKey(ProductVariant, on_delete=models.DO_NOTHING, verbose_name='Product')
    productOrderedProductQuantity = models.PositiveIntegerField(verbose_name='Quantity')
    productOrderedProductsvendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Vendor')
    productOrderedOrNot = models.BooleanField(default=False,verbose_name='Ordered')
    productOrderTotalPrice = models.PositiveBigIntegerField(default=0, verbose_name='Price (Exc. Disc)')
    productOrderFinalPrice = models.PositiveBigIntegerField(
        default=0, verbose_name='Price (Inc. Disc)')
    productOrderSavings = models.PositiveBigIntegerField(
        default=0, verbose_name='Saving (INR.)')

    productVariantOrderTax=models.PositiveIntegerField(default=0,verbose_name='Tax (%)')
    productVariantOrderTaxPrice=models.PositiveIntegerField(default=0,verbose_name='Tax Amount (Rs.)')
    productVariantOrderFinalPriceAfterTax=models.IntegerField(verbose_name='Price (After Tax)',blank=True,null=True)

    slug = models.SlugField(unique=True, blank=True)

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i+1]))
        return slugs

    def save(self, *args, **kwargs):
        # if self.orderedOrNot == False:
        #     raise Exception("Something went wrong")
        self.slug = slugify(self.id)
        req = get_request().user
        self.productOrderedByCustomer = req
        vendorofproduct = ProductVariant.objects.get(id=self.productOrderedProducts.id)
        self.productOrderedProductsvendor = vendorofproduct.variantProduct.productVendor
        super(ProductOrder, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.productOrderedByCustomer)+' - '+str(self.productOrderedProducts)

    class Meta:
        verbose_name = 'Product Order'

class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlistByCustomer = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,verbose_name='Customer')
    wishlistProducts = models.ManyToManyField(
        ProductVariant, blank=True, verbose_name='Products')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.wishlistByCustomer)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Wishlist, self).save(*args, **kwargs)

    def getWishlistProducts(self):
        return " | ".join([str(cp) for cp in self.wishlistProducts.all()])

    getWishlistProducts.short_description = 'Products'


class Compare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compareByCustomer = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,verbose_name='Customer')
    compareProducts = models.ManyToManyField(
        ProductVariant, blank=True, verbose_name='Products')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.compareByCustomer)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Compare, self).save(*args, **kwargs)

    def getCompareProducts(self):
        return " | ".join([str(i.variantProduct.productName) for i in self.compareProducts.all()])

    getCompareProducts.short_description = "Products"