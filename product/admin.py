from django.contrib import admin
from django import forms
from .models import AttributeName, AttributeValue, ProductMeta, ProductVariant, ProductAttributes, MultipleImages, Product, ProCategory, ProBrand, ProUnit, ProVideoProvider, ProductReview,DeliveryOption
from mptt.admin import MPTTModelAdmin
from django.db.models import Sum



# Register your models here.

class MultipleImageInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Count the number of forms that have a value in the "DELETE" field
        deleted_forms_count = 0
        for form in self.forms:
            if form.cleaned_data.get('DELETE') is True:
                deleted_forms_count += 1

        # If all forms are marked for deletion, raise a validation error
        if deleted_forms_count == self.total_form_count():
            raise forms.ValidationError(
                'You cannot delete all images. At least one image is required.')


class MultipleImageInline(admin.StackedInline):
    model = MultipleImages
    formset = MultipleImageInlineFormSet
    readonly_fields = ('id', 'image_tag',)
    extra = 0
    min_num = 1
    # max_num = 1
    validate_min = True
    verbose_name_plural = 'Images'
    
    
class ProductVariantAdminInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Create a dictionary to track the product variants for each variantProduct
        variant_products = {}

        # Count the number of forms that have a value in the "DELETE" field
        deleted_forms_count = 0
        for form in self.forms:
            if form.cleaned_data.get('DELETE') is True:
                deleted_forms_count += 1

        # If all forms are marked for deletion, raise a validation error
        if deleted_forms_count == self.total_form_count():
            raise forms.ValidationError('You cannot delete all product. At least one product is required.')

        for form in self.forms:
            variant_product = form.cleaned_data.get('variantProduct')
            variant_attributes = form.cleaned_data.get('productVariantAttribute')

            if variant_attributes:
                if variant_product and variant_attributes:
                    # Check if the variantProduct is already in the dictionary
                    if variant_product.pk in variant_products:
                        existing_attributes = variant_products[variant_product.pk]

                        # Compare the attributes of the current form with the existing attributes
                        if set(variant_attributes) == set(existing_attributes):
                            raise forms.ValidationError('Multiple product variants of the same product with similar attributes are not allowed.')
                    else:
                        # Add the variantProduct and attributes to the dictionary
                        variant_products[variant_product.pk] = variant_attributes
                
                                
            allAttributeFromProductVariants = []
            for form in self.forms:
                variant_attributes = form.cleaned_data.get('productVariantAttribute')
                if variant_attributes:
                    for attribute in variant_attributes:
                        allAttributeFromProductVariants.append(attribute)

            uniqueAttributeNames = []
            for attribute in allAttributeFromProductVariants:
                if attribute.attributeName not in uniqueAttributeNames:
                    uniqueAttributeNames.append(attribute.attributeName)

            for form in self.forms:
                variant_attributes = form.cleaned_data.get('productVariantAttribute')
                if variant_attributes:
                    attributeListOfSingleProductVariant = []
                    for attribute in variant_attributes:
                        attributeListOfSingleProductVariant.append(attribute.attributeName)
                    for attribute in uniqueAttributeNames:
                        if attribute not in attributeListOfSingleProductVariant:
                            raise forms.ValidationError('Each product varint must have all attribute which present in other product variant.')
            
            # Call the clean_productVariantAttribute method for each form in the formset
            for form in self.forms:
                # try:
                self.clean_productVariantAttribute(form)
                # except:
                #     raise forms.ValidationError('Something went wrong.')
                    

    # Additional logic for clean_productVariantAttribute
    def clean_productVariantAttribute(self, form):
        selected_attributes = form.cleaned_data.get('productVariantAttribute')
        variant_product_type = form.cleaned_data.get('variantProduct')
        
        if variant_product_type is not None:
            variant_product_type = variant_product_type.productType

            
            if variant_product_type == 'Classified' and not selected_attributes:
                raise forms.ValidationError('You must select at least one attribute for Classified products.')
            
            if selected_attributes:
                attribute_names = set()
                for attribute in selected_attributes:
                    if attribute.attributeName in attribute_names:
                        raise forms.ValidationError("You can select only one attribute from the same attribute category.")
                    attribute_names.add(attribute.attributeName)
            return selected_attributes
        
        
        
class ProductVariantAdminInline(admin.StackedInline):
    model = ProductVariant
    formset = ProductVariantAdminInlineFormSet
    # form = ProductVariantForm

    exclude = ['slug', 'productVariantDiscountPrice', 'productVariantFinalPrice',
               'productVariantTaxPrice', 'productVariantFinalPriceAfterTax', 'productVariantStockStatus']
    readonly_fields = ('id',)
    list_display = ['id', 'variantProduct', 'productVariantAttribute', 'productVariantQuantity', 'productVariantStockStatus', 'productVariantPrice', 'productVariantDiscount',
                    'productVariantDiscount', 'productVariantDiscountPrice', 'productVariantFinalPrice', 'productVariantTax', 'productVariantTaxPrice', 'productVariantFinalPriceAfterTax']
    list_filter = ['productVariantAttribute']

    verbose_name_plural = 'Product'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'productVariantQuantity': forms.TextInput(attrs={'placeholder': 'Enter Quantity'}),
            'productVariantPrice': forms.TextInput(attrs={'placeholder': 'Enter Price'}),
            'productVariantDiscount': forms.TextInput(attrs={'placeholder': 'Enter Discount Percentage Eg. 20'}),
            'productVariantTax': forms.TextInput(attrs={'placeholder': 'Enter Tax Percentage Eg. 18'}),
        }
        return super().get_form(request, obj, **kwargs)

    extra = 0
    min_num = 1
    # max_num = 1
    validate_min = True

admin.site.register(ProductVariant,
                    # 'variantProduct__productType' ,
                    list_display=['variantProduct', 'productVariantQuantity', 'productVariantStockStatus', 'productVariantPrice', 'productVariantDiscount',
                                  'productVariantDiscountPrice', 'productVariantFinalPrice', 'productVariantTax', 'productVariantTaxPrice', 'productVariantFinalPriceAfterTax', 'productVariantCreatedAt'],
                    list_filter=['variantProduct'],
                    search_fields=["variantProduct__productName"],
                    ordering=['-productVariantCreatedAt'],
                    list_per_page=10,
                    )

class ProductAdmin(admin.ModelAdmin):
   
    exclude = ['slug','productVendor', 'productNoOfReview', 'productStatus',
               'productRatingCount', 'productFinalRating', 'productEndDate', 'productSoldQuantity']
    # 'product_image',
    list_display = ['productName','proCategory','productType', 'productBrand', 'total_quantity','original_price','discount_percentage','discounted_price', 'productStatus', 
                      'sold_quantity', 'productUpdatedAt']
    ordering = ['-productUpdatedAt']
    list_filter = ['proCategory', 'productBrand']
    inlines = [ProductVariantAdminInline, MultipleImageInline]
    readonly_fields = ()
    list_per_page=10

    def get_queryset(self, request):

        if request.user.is_vendor:
            queryset = super(ProductAdmin, self).get_queryset(request)
            return queryset.filter(productVendor=request.user)
        else:
        # if request.user.is_superuser:
            queryset = super(ProductAdmin, self).get_queryset(request)
            return queryset
        

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'productName': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
            'productVideoLink': forms.TextInput(attrs={'placeholder': 'Add Video Link'}),
            'productWeight': forms.TextInput(attrs={'placeholder': 'Enter Weight'}),
            'productDimension': forms.TextInput(attrs={'placeholder': 'Enter Dimension'}),
            'productSKU': forms.TextInput(attrs={'placeholder': 'Enter SKU'}),
        }
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='Discounted Price')
    def discounted_price(self, obj):
        # return 'Discounted Price'
        if obj.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=obj)
            cheapest_product = min(productVariants, key=lambda x: x.productVariantFinalPrice)
            most_expensive_product = max(productVariants, key=lambda x: x.productVariantFinalPrice)
            return f"{cheapest_product.productVariantFinalPrice} - {most_expensive_product.productVariantFinalPrice}"
        
        if obj.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=obj).first()
            return str(productVariant.productVariantFinalPrice)
    
    @admin.display(description='Original Price')
    def original_price(self, obj):
        # return 'Original Price'
        if obj.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=obj)
            cheapest_product = min(productVariants, key=lambda x: x.productVariantPrice)
            most_expensive_product = max(productVariants, key=lambda x: x.productVariantPrice)
            return f"{cheapest_product.productVariantPrice} - {most_expensive_product.productVariantPrice}"
        
        if obj.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=obj).first()
            return str(productVariant.productVariantPrice)
        
    @admin.display(description='Discount %')
    def discount_percentage(self, obj):
        # return 'Discount Percentage'
        if obj.productType == "Classified":
            productVariants = ProductVariant.objects.filter(variantProduct=obj)
            product_with_lowest_discount = min(productVariants, key=lambda x: x.productVariantDiscount)
            product_with_highest_discount = max(productVariants, key=lambda x: x.productVariantDiscount)
            
            if str(product_with_lowest_discount.productVariantDiscount) == str(product_with_highest_discount.productVariantDiscount):
                return str(product_with_lowest_discount.productVariantDiscount)+ "%"
            else:
                return str(product_with_lowest_discount.productVariantDiscount) + "% - " + str(product_with_highest_discount.productVariantDiscount) + "%"
        
        if obj.productType == "Simple":
            productVariant = ProductVariant.objects.filter(variantProduct=obj).first()
            return str(productVariant.productVariantDiscount) + "%" 
        
    @admin.display(description='Total Sold')
    def sold_quantity(self, obj):
        productMetaObj=ProductMeta.objects.get(product=obj)
        return str(productMetaObj.productSoldQuantity)
    
    @admin.display(description='Quantity')
    def total_quantity(self, obj):
        productVariants=ProductVariant.objects.filter(variantProduct=obj)
        total_quantity=productVariants.aggregate(Sum('productVariantQuantity'))['productVariantQuantity__sum']
        return str(total_quantity)
        
    

admin.site.register(Product, ProductAdmin,
                    list_per_page=10)

admin.site.register(DeliveryOption)


class ProductReviewAdmin(admin.ModelAdmin):
    exclude = ['productReviewByCustomer']
    search_fields = ['productName', 'productReview', 'productRatings']
    list_display = ['productName', 'productReview', 'productRatings','productReviewByCustomer']

    def get_queryset(self, request):
        if request.user.is_vendor:
            queryset = super(ProductReviewAdmin, self).get_queryset(request)
            return queryset.filter(productName__productVendor=request.user)
        else:
        # if request.user.is_superuser:
            queryset = super(ProductReviewAdmin, self).get_queryset(request)
            return queryset

admin.site.register(ProductReview, ProductReviewAdmin)

admin.site.register(
    ProCategory,
    MPTTModelAdmin,
    exclude=['slug', 'categoryTotalProduct'],
    list_display=['categoryName',
                  'categoryProductCommission', 'categoryTotalProduct'],
    # list_filter = ['categoryName',],
    search_fields=['categoryName',],
    list_per_page=10
)

class ProductBrandAdmin(admin.ModelAdmin):
    exclude = ['slug', 'brandTotalProduct']
    list_display = ['brandName', 'brandTotalProduct']
    search_fields = ['brandName', 'brandTotalProduct']

admin.site.register(ProBrand, ProductBrandAdmin,
                        list_per_page=10
)
admin.site.register(
    ProUnit,
    exclude=['slug'],
    # list_filter = ['unitName'],
    search_fields=['unitName',]
)
admin.site.register(
    ProVideoProvider,
    exclude=['slug'],
)



class AttributeNameAdminForm(forms.ModelForm):
    class Meta:
        model = AttributeName
        fields = '__all__'

    def clean_attributeName(self):
        attributeName = self.cleaned_data['attributeName']
        lowercase_attributeName = attributeName.lower()

        # Check if any AttributeName object with the same lowercase attributeName exists
        existingAttributeName = AttributeName.objects.all().exclude(
            attributeName=attributeName)
        if existingAttributeName.filter(attributeName__iexact=lowercase_attributeName).exists():
            raise forms.ValidationError(
                'An Attribute Name with a similar value already exists.')

        return attributeName

class AttributeValueAdminForm(forms.ModelForm):
    class Meta:
        model = AttributeValue
        fields = '__all__'

    def clean_attributeValue(self):
        attributeName = self.cleaned_data['attributeName']
        attributeValue = self.cleaned_data['attributeValue']
        lowercase_attributeValue = attributeValue.lower()

        # Check if any AttributeValue object with the same attributeName and lowercase attributeValue exists

        try:
            currentAttributeName = AttributeName.objects.get(
                attributeName=attributeName)
            currentAttributeName = AttributeName.objects.get(
                attributeName=attributeName)
            currentAttributeValue = AttributeValue.objects.all().exclude(
                attributeName=currentAttributeName, attributeValue=attributeValue)
            if currentAttributeValue.filter(attributeValue__iexact=lowercase_attributeValue).exists():
                raise forms.ValidationError(
                    'An Attribute Value with a similar value already exists for the selected Attribute.')
            return attributeValue

        except AttributeName.DoesNotExist:
            # Handle the case where currentAttributeName does not exist
            return attributeValue

class AttributeValueAdminInline(admin.StackedInline):
    form = AttributeValueAdminForm
    model = AttributeValue
    exclude = ['slug', 'id', 'createdAt']
    readonly_fields = ('id',)
    extra = 0
    min_num = 1
    validate_min = True

class AttributeNameAdmin(admin.ModelAdmin):
    form = AttributeNameAdminForm
    exclude = ['slug', 'id', 'createdAt']
    list_display = ['attributeName', 'atribute_value','createdAt']
    ordering = ['-createdAt']
    verbose_name_plural = 'Attributes'
    inlines = [AttributeValueAdminInline]
    
    @admin.display(description='Values')
    def atribute_value(self, obj):
        attributeValues=AttributeValue.objects.filter(attributeName=obj)
        valueList=" , ".join([str(value.attributeValue) for value in attributeValues])
        return "No Value Yet" if valueList=="" else valueList  
        # return str(total_quantity)

admin.site.register(AttributeName, AttributeNameAdmin)
