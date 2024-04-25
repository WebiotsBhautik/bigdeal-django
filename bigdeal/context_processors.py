import decimal
from random import shuffle
from accounts.models import Admin, CustomUser
from order.models import ProductOrder,Order,OrderPayment
from payment.models import Wallet
from product.models import ProCategory, Product,ProBrand, ProductMeta,ProductReview
from django.db.models import Sum

def dashboardData(request):
    totalUser = CustomUser.objects.values('id').count()
    totalProductOrders=ProductOrder.objects.values('id').count()
    totalProductReviews=ProductReview.objects.values('id').count()
    totalVendors=CustomUser.objects.filter(is_vendor=True).count()
    totalRevenue = Order.objects.aggregate(Sum('orderTotalPrice'))['orderTotalPrice__sum']
    if totalRevenue is None:
        totalRevenue='0.00'
    recentPayments=OrderPayment.objects.all().order_by('-id')[:10]

    # Access Admin Superuser
    superUser = CustomUser.objects.get(email="admin@gmail.com")
    adminInstance = Admin.objects.get(admin=superUser)
    adminWalletBalance=adminInstance.adminWalletBalance
    adminTotalCommissionProfit=adminInstance.adminCommissionProfit

    topSoldProducts = ProductMeta.objects.all().order_by('-productSoldQuantity')[:8]
    sold_product_labels=[]
    sold_product_count=[]
    for product in topSoldProducts:
        sold_product_labels.append(product.product.productName)
        sold_product_count.append(product.productSoldQuantity)

    mostPopularCategories = ProCategory.objects.all().order_by('-categoryTotalProduct')[:8]
    popular_categories_labels=[]
    popular_categories_count=[]
    for category in mostPopularCategories:
        popular_categories_labels.append(category.categoryName)
        popular_categories_count.append(category.categoryTotalProduct)

    rated_product_labels=[]
    rated_product_count=[]
    topRatedProducts = Product.objects.all().order_by('-productFinalRating')[:10]
    for product in topRatedProducts:
        rated_product_labels.append(product.productName)
        rated_product_count.append(product.productFinalRating)

    brand_labels=[]
    brand_product_count=[]
    topBrands= ProBrand.objects.all().order_by('-brandTotalProduct')[:5]
    for brand in topBrands:
        brand_labels.append(brand.brandName)
        brand_product_count.append(brand.brandTotalProduct)

    superuser=CustomUser.objects.get(email='admin@gmail.com')
    admin=Admin.objects.get(admin=superuser)
    
    
    vendorWaletBalance=None
    totalVendorProductOrders=None
    totalRevenueForVendor=None
    if request.user.is_authenticated:
        if request.user.is_vendor:
            user = CustomUser.objects.get(id=request.user.id)
            userInstance = Wallet.objects.get(walletByUser=user)
            vendorWaletBalance=userInstance.walletBalance
            
            totalVendorProductOrders=ProductOrder.objects.filter(productOrderedProductsvendor=user).values('id').count()
            
            vendorsAllOrder = ProductOrder.objects.filter(productOrderedProductsvendor=user)
            totalRevenueForVendor=vendorsAllOrder.aggregate(Sum('productOrderFinalPrice'))['productOrderFinalPrice__sum']
            if totalRevenueForVendor is None:
                totalRevenueForVendor='0.00'
    
    dashboardData = {
        "adminWalletBalance":adminWalletBalance,
        "adminTotalCommissionProfit":adminTotalCommissionProfit,
        'totalUser':totalUser,
        'totalProductOrders':totalProductOrders,
        'totalProductReviews':totalProductReviews,
        "totalVendors":totalVendors,
        'totalRevenue':totalRevenue,
        'sold_product_labels': sold_product_labels,
        'sold_product_count': sold_product_count,
        'popular_categories_labels': popular_categories_labels,
        'popular_categories_count': popular_categories_count,
        'rated_product_labels':rated_product_labels,
        'rated_product_count':rated_product_count,
        'brand_labels':brand_labels,
        'brand_product_count':brand_product_count,
        'recentPayments':recentPayments,
        'admin':admin,
        
        'vendorWaletBalance':vendorWaletBalance,
        'totalVendorProductOrders':totalVendorProductOrders,
        'totalRevenueForVendor':totalRevenueForVendor,
        
        
        }
    return dashboardData 
