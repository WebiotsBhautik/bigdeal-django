import uuid
from django.db import models
from django.utils.text import slugify
from product.models import  ProductVariant
from accounts.models import CustomUser
from ckeditor.fields import RichTextField
from accounts.get_username import get_request
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

# Create your models here.

class BannerTheme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerThemeName = models.CharField(max_length=250, verbose_name='Name')
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
    titleOne = models.CharField(
        max_length=255, verbose_name='Title One')
    titleTwo = models.CharField(
        max_length=255, blank=True, verbose_name='Title Two')
    titleThree = models.CharField(
        max_length=255, blank=True, verbose_name='Title Three')
    titleFour = models.CharField(
        max_length=255, blank=True, verbose_name='Title Four')
    
    
    def __str__(self):
        return str(self.bannerTheme)+" | "+str(self.bannerType)+" | "+str(self.bannerProduct)

    class Meta:
        verbose_name = 'Banner'
    
    
    
    
        
        
        
    
