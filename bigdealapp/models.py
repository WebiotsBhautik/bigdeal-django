import uuid
from django.db import models
from django.utils.text import slugify
from product.models import  ProductVariant
from accounts.models import CustomUser
from ckeditor.fields import RichTextField
from accounts.get_username import get_request
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
from order.models import Order

# Create your models here.

class BannerTheme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerThemeName = models.CharField(max_length=250, verbose_name='Name')
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Status")
    
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
        self.slug = slugify(self.bannerThemeName)
        super(BannerTheme, self).save(*args,**kwargs)
        
        
    def __str__(self):
        return self.bannerThemeName
    
    
    class Meta:
        verbose_name = 'Theme'
        

class BannerType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerTypeName = models.CharField(max_length=250, verbose_name='Name')
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
        self.slug = slugify(self.bannerTypeName)
        super(BannerType, self).save(*args, **kwargs)

    def __str__(self):
        return self.bannerTypeName

    class Meta:
        verbose_name = 'Banner Type'
        
        
class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerTheme = models.ForeignKey(
        BannerTheme, on_delete=models.CASCADE, verbose_name='Theme')
    bannerType = models.ForeignKey(
        BannerType, on_delete=models.CASCADE, verbose_name='Type')
    bannerProduct = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, verbose_name='Product')
    bannerImage = models.ImageField(
        upload_to='fashion/banner', verbose_name='Image')
    bannerImageTwo = models.ImageField(
        upload_to='fashion/banner', verbose_name='Optional Image', blank=True, null=True)
    titleOne = models.CharField(
        max_length=255, verbose_name='Title One')
    titleTwo = models.CharField(
        max_length=255, blank=True, verbose_name='Title Two')
    titleThree = models.CharField(
        max_length=255, blank=True, verbose_name='Title Three')
    titleFour = models.CharField(
        max_length=255, blank=True, verbose_name='Title Four')
    bannerDescription = RichTextField(
        blank=True, null=True, verbose_name='Description')
    
    
    def __str__(self):
        return str(self.bannerTheme)+" | "+str(self.bannerType)+" | "+str(self.bannerProduct)

    class Meta:
        verbose_name = 'Banner'
        
        
class BlogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categoryName=models.CharField(max_length=255,verbose_name='Name')
    categoryImage=models.ImageField(verbose_name='Image',upload_to='fashion/blog/category')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
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
        self.slug = slugify(self.id)
        super(BlogCategory, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.categoryName)

    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        
        
class Blog(models.Model):
    BLOG_STATUS = ((0,"Draft"),(1,"Publish"))
    POPULAR_STATUS = ((0,"False"),(1,"True"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blogAuthor=models.ForeignKey(CustomUser,on_delete=models.CASCADE,blank=True,verbose_name='Author')
    blogCategory=models.ForeignKey(BlogCategory,on_delete=models.CASCADE,blank=True,verbose_name='Category')
    blogTitle=models.CharField(max_length=255,verbose_name='Title')
    blogSubTitle=models.CharField(max_length=255,verbose_name='Sub Title')
    blogImage=models.ImageField(verbose_name='Image',upload_to='fashion/blag/blogimage')
    blogDescription=RichTextField(verbose_name='Description')
    blogStatus = models.IntegerField(choices=BLOG_STATUS, default=0,verbose_name='Published or Draft')
    popularBlog = models.IntegerField(choices=POPULAR_STATUS,default=0,verbose_name='Popular Blog Or Not')
    status=models.BooleanField(default=True, verbose_name='Status')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
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
        req = get_request().user
        self.blogAuthor=req
        self.slug = slugify(self.id)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.blogSubTitle)

    class Meta:
        verbose_name = 'Blog'
        
        
        
class BlogComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commentOfBlog=models.ForeignKey(Blog, on_delete=models.CASCADE,blank=True,verbose_name='Blog')
    commentByUser=models.ForeignKey(CustomUser,on_delete=models.CASCADE,blank=True,verbose_name='User')
    comment=models.CharField(max_length=255,verbose_name='Comment')
    status=models.BooleanField(default=True, verbose_name='Status')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
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
        self.slug = slugify(self.id)
        req = get_request().user
        self.commentByUser=req
        super(BlogComment, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.commentByUser)

    class Meta:
        verbose_name = 'Comment'
        
        
class ContactUs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    contactUsEmail = models.EmailField(max_length=200,verbose_name='Email')
    contactUsName = models.CharField(max_length=200,verbose_name='Name')
    contactUsNumber = models.CharField(validators=[phoneNumberRegex], max_length=16, unique=False, verbose_name='Contact No.')
    contactUsComment = models.TextField(max_length=255,verbose_name='Comment')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')

    def __str__(self):
        return self.contactUsName
    
    class Meta:
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'
        
        
class Coupon(models.Model):
    couponTypeChoices = [('Fixed','Fixed'),('Percentage','Percentage'),]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    couponCode = models.CharField(max_length=200, unique=True, verbose_name='Code')
    couponType = models.CharField(max_length=255, choices=couponTypeChoices, verbose_name='Type')
    numOfCoupon = models.PositiveIntegerField(default=0,verbose_name='Num. of Coupons')
    couponDiscountOrFixed = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(100)],verbose_name='Amount / Discount (%)')
    minAmount = models.DecimalField(default=0, max_digits=10, decimal_places=2,blank=True,null=True,verbose_name='Minimum Amount')
    expirationDateTime = models.DateTimeField(verbose_name='Expiration Date')
    usageLimit = models.PositiveIntegerField(default=1,verbose_name='Usage Limit')
    couponDescription = models.TextField(verbose_name='Description')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    
    def __str__(self):
        return self.couponCode

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        
        
        
class CouponHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='Coupon')
    couponHistoryByUser = models.ForeignKey(CustomUser, on_delete=models.CASCADE,verbose_name='User')
    couponHistoryByOrder = models.ForeignKey(Order,on_delete=models.CASCADE, verbose_name='Order')
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updatedAt = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return str(self.coupon)

    class Meta:
        verbose_name = 'Coupon History'
        verbose_name_plural = 'Coupon History'