from datetime import timedelta, timezone
from datetime import *
from django.forms import ValidationError
from django.utils import timezone
from datetime import date
# import pytz
import uuid
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey
from accounts.models import CustomUser
from accounts.get_username import get_request
from django.utils.safestring import mark_safe
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.


class ProCategory(MPTTModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categoryName = models.CharField(max_length=255, verbose_name='Name')
    categoryImage = models.ImageField(
        verbose_name='Image', upload_to='fashion/category')
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True, on_delete=models.CASCADE)
    categoryProductCommission = models.DecimalField(default=0, max_digits=10, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ], decimal_places=2, verbose_name='Commission %', blank=True, null=True)
    categoryTotalProduct = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='No. of Product')
    slug = models.SlugField(unique=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['categoryName']

    class Meta:
        unique_together = (('parent', 'slug',))
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

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
        self.slug = slugify(self.categoryName)
        super(ProCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.categoryName

    def get_all_parents(self):
        return self.get_ancestors()
    
    
    @property
    def category_products_price_range(self):
        productVariants = ProductVariant.objects.filter(variantProduct__proCategory=self)
        if productVariants.exists():
            # To get the lowest price,
            cheapest_product = min(productVariants, key=lambda x: x.productVariantFinalPrice)

            # To get the highest price,
            most_expensive_product = max(productVariants, key=lambda x: x.productVariantFinalPrice)
            price_range = f"{cheapest_product.productVariantFinalPrice}-{most_expensive_product.productVariantFinalPrice}"
            return price_range
        else:
            return ""

    
    
    
class ProductAttributes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attributeColor = models.CharField(max_length=255, verbose_name='Color')
    attributeSize = models.CharField(max_length=255, verbose_name='Size')
    attributeName=models.CharField(max_length=255, verbose_name='Attribute',unique=True,blank=True,null=True)
    attributeImage = models.ImageField(verbose_name='Image', upload_to='fashion/product/attribute')
    attributeTotalProduct = models.PositiveIntegerField(blank=True, null=True, default=0, verbose_name='No. of Attrbute')
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = (('attributeColor', 'attributeSize'))
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'
        
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
        self.slug = slugify(self.id)
        self.attributeName= str(self.attributeSize)+" - Size | "+str(self.attributeColor)+" - Color"
        super(ProductAttributes, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.attributeName)
    
    
class ProBrand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brandName = models.CharField(max_length=255, verbose_name='Brand Name')
    brandTotalProduct = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='No. of Product')
    slug = models.SlugField(unique=True, blank=True)

            
    def save(self, *args, **kwargs):
        self.slug = slugify(self.brandName)

        # Check if a brand with the same name already exists
        existing_brand = ProBrand.objects.filter(brandName=self.brandName).exclude(pk=self.pk).first()
        if existing_brand:
            raise ValueError("Brand with this name already exists.")
        
        super(ProBrand, self).save(*args, **kwargs)

    def __str__(self):
        return self.brandName

    class Meta:
        verbose_name = 'Brand'

class ProUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unitName = models.CharField(max_length=255, verbose_name='Unit')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.unitName)
        super(ProUnit, self).save(*args, **kwargs)

    def __str__(self):
        return self.unitName

    class Meta:
        verbose_name = 'Unit'

class ProVideoProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    videoProviderName = models.CharField(
        max_length=255, verbose_name='Video Provider')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.videoProviderName)
        super(ProVideoProvider, self).save(*args, **kwargs)

    def __str__(self):
        return self.videoProviderName

    class Meta:
        verbose_name = 'Video Provider'
        
        
class DeliveryOption(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

        
        
        
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productVendor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Vendor')
    productTypeChoices = [('Simple', 'Simple'), ('Classified', 'Classified')]
    productName = models.CharField(max_length=255, verbose_name='Name')
    productType = models.CharField(
        max_length=255, choices=productTypeChoices, verbose_name='Type')
    productStatus = models.BooleanField(default=True, verbose_name='Status')
    proCategory = TreeForeignKey(ProCategory, on_delete=models.CASCADE, verbose_name='Category')
    productBrand = models.ForeignKey(
        ProBrand, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Brand')
    productUnit = models.ForeignKey(
        ProUnit, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Unit')
    productDescription = RichTextField(
        blank=True, null=True, verbose_name='Description')
    productImageFront = models.ImageField(
        verbose_name='Front Image', upload_to='fashion/product/front')
    productImageBack = models.ImageField(
        verbose_name='Back Image', upload_to='fashion/product/back')
    productThumImage = models.ImageField(
        verbose_name='Thumbnail', upload_to='fashion/product/thumbnail')
    productVideoProvider = models.ForeignKey(
        ProVideoProvider, on_delete=models.CASCADE, verbose_name='Video Provider', blank=True, null=True)
    productVideoLink = models.CharField(
        max_length=255, verbose_name='Video Link', blank=True, null=True)
    productWeight = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name='Weight')
    productDimension = models.CharField(
        max_length=255, verbose_name='Dimensions (cm)', blank=True, null=True)
    productSKU = models.CharField(
        max_length=255, verbose_name='SKU', blank=True, null=True)
    productUpsells = models.CharField(
        max_length=255, verbose_name='Upsells', blank=True, null=True)
    productCrossSells = models.ManyToManyField(
        to='product.ProductVariant', blank=True, verbose_name='Cross sell') 
    productCreatedAt = models.DateTimeField(auto_now_add=True)
    productUpdatedAt = models.DateTimeField(
        auto_now=True, verbose_name='Updated At')
    productEndDate = models.DateTimeField(blank=True, null=True)
    productNoOfReview = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='No. of Review')
    productRatingCount = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='Rating Count')
    productFinalRating = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='Rating (5)')
    deliveryOption = models.ManyToManyField(DeliveryOption, blank=True, verbose_name='Delivery Option')
    productSoldQuantity = models.PositiveIntegerField(
        blank=True, null=True, default=0, verbose_name='Sold')
    slug = models.SlugField(max_length=255, blank=True)
    
    
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created for the first time
            self.slug = slugify(str(self.productName) + str(self.id))
            
            req = get_request().user
            self.productVendor = req

            # End date to display new product
            now = timezone.now()
            self.productEndDate = now + timedelta(days=5)
            
            if self.productType is None:
                self.productType = "Simple"

        if self.productType is None:
                self.productType = "Simple"
        
        super(Product, self).save(*args, **kwargs)
        
    

    def __str__(self):
        return self.productName
    


    class Meta:
        verbose_name = 'Product'

    @property
    def is_past_due(self):
        if self.productEndDate and date.today() > self.productEndDate.date():
            return True
        return False
    
    
    
    @property
    def product_price_range(self):
        if self.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=self)

            # To get the lowest price,
            cheapest_product = min(productVariants, key=lambda x: x.productVariantFinalPrice)

            # To get the highest price,
            most_expensive_product = max(productVariants, key=lambda x: x.productVariantFinalPrice)
            return str(cheapest_product.productVariantFinalPrice), str(most_expensive_product.productVariantFinalPrice)

        if self.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=self).first()
            return str(productVariant.productVariantFinalPrice)

    @property
    def product_discount_range(self):
        if self.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=self)

            # To get the lowest price,
            product_with_lowest_discount = min(productVariants, key=lambda x: x.productVariantDiscount)

            # To get the highest price,
            product_with_highest_discount = max(productVariants, key=lambda x: x.productVariantDiscount)
            
            if str(product_with_lowest_discount.productVariantDiscount) == str(product_with_highest_discount.productVariantDiscount):
                return str(product_with_lowest_discount.productVariantDiscount)+ "% off"
            else:
                return str(product_with_lowest_discount.productVariantDiscount) + "% - " + str(product_with_highest_discount.productVariantDiscount) + "% off"

        if self.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=self).first()
            return str(productVariant.productVariantDiscount) + "% off" 
        
    
    @property
    def product_actual_price_range(self):
        if self.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=self)

            # To get the lowest price,
            cheapest_product = min(productVariants, key=lambda x: x.productVariantPrice)

            # To get the highest price,
            most_expensive_product = max(productVariants, key=lambda x: x.productVariantPrice)
            
            return str(cheapest_product.productVariantPrice), str(most_expensive_product.productVariantPrice)

        if self.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=self).first()
            return str(productVariant.productVariantPrice)
    
    
    
class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productVariantStockStatus = [('In Stock', 'In Stock'), ('Out Of Stock', 'Out Of Stock'), ('On Backorder', 'On Backorder')]
    variantProduct = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    productVariantAttribute = models.ManyToManyField(to='product.AttributeValue', blank=True, verbose_name='Attribute')
    productVariantQuantity = models.PositiveIntegerField(verbose_name='Quantiy')
    productVariantStockStatus = models.CharField(max_length=255, choices=productVariantStockStatus, verbose_name='Stock Status', blank=True, null=True)
    productVariantPrice = models.PositiveIntegerField(verbose_name='Original Price')
    productVariantDiscount = models.PositiveIntegerField(verbose_name='Discount (%)')
    productVariantDiscountPrice = models.PositiveIntegerField(default=0, verbose_name='Savings (Rs.)')
    productVariantFinalPrice = models.PositiveIntegerField(default=0, verbose_name='Discounted Price', blank=True, null=True)
    productVariantTax = models.PositiveIntegerField(verbose_name='Tax (%)')
    productVariantTaxPrice = models.PositiveIntegerField(default=0, verbose_name='Tax Amount (Rs.)')
    productVariantFinalPriceAfterTax = models.PositiveIntegerField(verbose_name='Final Price', blank=True, null=True)
    productVariantCreatedAt = models.DateTimeField(auto_now_add=True)
    productVariantUpdatedAt = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.variantProduct)+str(self.id))

        if self.variantProduct.productType == "Simple":
            self.productVariantAttribute.clear()

        # Quantity management
        if self.productVariantQuantity > 0:
            self.productVariantStockStatus = 'In Stock'

        # Final price calculation after discount
        productVariantDis = self.productVariantDiscount
        productVariantPric = self.productVariantPrice
        productVariantDiscAmmount = (round((productVariantPric*productVariantDis)/100))
        self.productVariantFinalPrice = productVariantPric-productVariantDiscAmmount
        self.productVariantDiscountPrice = productVariantDiscAmmount

        # Final price calculation after tax
        productVariantTaxVar = self.productVariantTax
        productVariantFinalPriceBeforeTax = self.productVariantFinalPrice
        variantTaxAmount = (round((productVariantFinalPriceBeforeTax*productVariantTaxVar)/100))
        self.productVariantFinalPriceAfterTax = productVariantFinalPriceBeforeTax + variantTaxAmount
        self.productVariantTaxPrice = variantTaxAmount
        super(ProductVariant, self).save(*args, **kwargs)

    def __str__(self): 
        if str(self.variantProduct.productType) == "Simple":
            return str(self.variantProduct.productName)
        if str(self.variantProduct.productType) == "Classified":
            attribute_values = ', '.join(str(attribute) for attribute in self.productVariantAttribute.all())
            return str(f"{self.variantProduct.productName} | {attribute_values}")
        
            
    class Meta:
        verbose_name = 'Variant'
        
        
class MultipleImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    multipleImageOfProduct = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True)
    multipleImages = models.ImageField(
        verbose_name='Images', null=True, upload_to='fashion/product/multipleimages')

    def __str__(self):
        return self.multipleImageOfProduct.productName

    def image_tag(self):
        if self.multipleImages.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.multipleImages.url))
        else:
            return "Nothing to Show"

    class Meta:
        verbose_name = 'Multiple Image'
        verbose_name_plural = 'Multiple Images'
        
        
class ProductMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Product")
    productSoldQuantity = models.PositiveIntegerField(blank=True, null=True, default=0, verbose_name='Sold')
    
    def __str__(self):
        return str(self.product)
    
    
class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productRatingsChoices = [('0', '0'), ('1', '1'),('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    productReviewByCustomer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, verbose_name='Customer')
    productName = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='Product Name')
    productReview = models.CharField(max_length=255, verbose_name='Review')
    productRatings = models.CharField(
        default=0, max_length=10, choices=productRatingsChoices, verbose_name='Rating')

    
    def save(self, *args, **kwargs):
        req = get_request().user

        product = Product.objects.get(id=self.productName.id)
        productNoOfReview=product.productNoOfReview

        if productNoOfReview == 0:
            product.productNoOfReview=1
            product.productRatingCount=int(self.productRatings)
            product.productFinalRating=int(self.productRatings)
            product.save()
        if productNoOfReview > 0:
            product.productNoOfReview = int(product.productNoOfReview) + 1
            product.productRatingCount = int(product.productRatingCount) + int(self.productRatings)
            totalStar=5*int(product.productNoOfReview)
            actualStar=int(product.productRatingCount)
            average=(5*actualStar)/totalStar
            product.productFinalRating=round(average)
            product.save()
        
        self.productReviewByCustomer = req
        super(ProductReview, self).save(*args, **kwargs)
        
    def update_product_rating(self):
        total_reviews = self.productreview_set.count()
        if total_reviews > 0:
            total_rating = sum([int(review.productRatings) for review in self.productreview_set.all()])
            self.productFinalRating = round(total_rating / total_reviews)
        else:
            self.productFinalRating = 0
        self.save()

    def __str__(self):
        return str(self.productName)

    class Meta:
        verbose_name = 'Review'
        
        
        
class AttributeName(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attributeName = models.CharField(max_length=255,unique=True,verbose_name='Attribute')
    slug = models.SlugField(unique=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.attributeName)
        super(AttributeName, self).save(*args, **kwargs)

    def __str__(self):
        return self.attributeName

class AttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attributeName=models.ForeignKey(AttributeName, on_delete=models.CASCADE, blank=True, verbose_name='Attribute')
    attributeValue = models.CharField(max_length=255,verbose_name='Value')
    attributeImage = models.ImageField(blank=True,null=True,verbose_name='Image', upload_to='fashion/product/attribute')
    slug = models.SlugField(unique=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')

    class Meta:
        unique_together = (('attributeName', 'attributeValue'))
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'
        
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
        self.slug = slugify(self.id)
        super(AttributeValue, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.attributeValue) + " - " + str(self.attributeName)
        
            
        
        
        
        
        
        
        
        

