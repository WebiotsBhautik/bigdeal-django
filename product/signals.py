from django.views.decorators.csrf import csrf_protect
from product.models import Product,ProBrand,ProCategory, ProductMeta, ProductReview, ProductVariant
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete,pre_delete

@receiver(post_save, sender=Product)
def brand_update_signal(sender, instance, created, **kwargs): 
    if created:
        brand=instance.productBrand
        obj=ProBrand.objects.get(brandName=brand)
        obj.brandTotalProduct=int(obj.brandTotalProduct)+int(1)
        obj.save()

@receiver(post_save, sender=Product)
def category_update_signal(sender, instance, created, **kwargs): 
    if created:
        category=instance.proCategory
        obj=ProCategory.objects.get(categoryName=category)
        obj.categoryTotalProduct=int(obj.categoryTotalProduct)+int(1)
        obj.save()
        
@receiver(post_save, sender=Product)
def signal_to_create_meta_product(sender, instance, created, **kwargs): 
    if created:
        ProductMeta.objects.create(product=instance)
        
@receiver(post_delete,sender=Product)
def signal_productcategory_totalproduct_management(sender,instance,*args,**kwargs):
    product_category = ProCategory.objects.get(id=instance.proCategory.id)
    if product_category.categoryTotalProduct >= 1:
        product_category.categoryTotalProduct = int(product_category.categoryTotalProduct)-int(1)
        product_category.save()

@receiver(post_delete,sender=Product)
def signal_productbrand_brandtotalproduct_management(sender,instance,*args,**kwargs):
    product_brand = ProBrand.objects.get(id=instance.productBrand.id)
    if product_brand.brandTotalProduct >= 1:
        product_brand.brandTotalProduct = int(product_brand.brandTotalProduct)-int(1)
        product_brand.save()

@receiver(post_save, sender=Product)
def signal_to_manage_variant_attribute(sender, instance, created, **kwargs): 
    if created:
        productType=instance.productType
        if productType == "Simple":
            variants=ProductVariant.objects.filter(variantProduct=instance)
            for variant in variants:
                variant.productVariantAttribute.clear()
                variant.save()

@receiver(post_delete,sender=ProductReview)
def signal_to_manage_number_of_review(sender,instance,*args,**kwargs):
    productId=instance.productName.id
    product=Product.objects.get(id=productId)
    product.productNoOfReview-=1
    product.save()


# @receiver(pre_delete, sender=Product)
# def product_pre_delete(sender, instance, **kwargs):
#     categoryName=instance.proCategory.categoryName
#     category=ProCategory.objects.get(categoryName=str(categoryName))
#     category.categoryTotalProduct=category.categoryTotalProduct-1
#     category.save()

