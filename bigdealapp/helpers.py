import json
from more_itertools import unique_everseen
from django.shortcuts import redirect, render
from product.models import AttributeName, Product, ProductAttributes, ProductVariant
from currency.models import Currency
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
# from random import randint
import math, random

def get_color_and_size_list(product, productVariants):
   
    colorDict = []
    sizeDict = []
    
    if product.productType == 'Classified':\

        for productVariant in productVariants:
            input_str = str(productVariant.productVariantAttribute.attributeName)


            parts = input_str.split("|")


            size_parts = parts[0].split(" - ")
            size_dict = {'fn': parts[0], 'sn': size_parts[0]}

            # split the second part to get the keys and values for the color dictionary
            color_parts = parts[1].split(" - ")
            color_dict = {'fn': parts[1], 'sn': color_parts[0],'img': str(productVariant.productVariantAttribute.attributeImage)}
          
            colorDict.append(color_dict)
            sizeDict.append(size_dict)
        
            # remove duplicates based on the 'fn' key in colorDict
            colorDict = list(unique_everseen(colorDict, key=lambda d: d['fn']))


            sizeDict = list(unique_everseen(sizeDict, key=lambda d: d['fn']))
            
    return colorDict, sizeDict

def GetUniqueProducts(AllProducts):
    ProductToSend = []
    for product in AllProducts:
        if len(ProductToSend):
            if not IsVariantPresent(ProductToSend,product):
                ProductToSend.append(product)
        else:
            ProductToSend.append(product)
    return ProductToSend

def IsVariantPresent(List,ValueToCheck):
    IsPresent = False
    for el in List:
        if el.variantProduct.id == ValueToCheck.variantProduct.id:
            IsPresent = True
            break
    return IsPresent

def GetRoute(Url,key,filters,request):
    Url+=key+'='
    try:
        if isinstance(filters, str):
            Url+=filters+','
        else:    
            for filter in filters:
                Url+=filter+','
    except Exception as e:
        print('=====> error <======',e)
        pass
    Url+='&'
    return Url 

def create_query_params_url(request,path):
    url=''
    prices = ''
    if request.method == "POST":
        selected_brands = request.POST.getlist('allbrand')
        selected_price = request.POST.get('pricefilter')

        if '-' in selected_price:
            prices = selected_price

         
        if '-' not in selected_price:
            prices = selected_price.split(';')

        url='/'+path+'?'
        
        urlStringList=[{"key":'brands',"value":selected_brands},{"key":"price","value":prices},]
        
        selectedAttributeList = []
        attributeList = [attribute.attributeName for attribute in AttributeName.objects.all()]
        for attribute in attributeList:
            dict={"key":attribute,"value":request.POST.getlist(attribute)}
            values=request.POST.getlist(attribute)
            for value in values:
                selectedAttributeList.append(value)
            urlStringList.append(dict)
        
        urlStringList.append({"key":"selectedAttribute","value":selectedAttributeList})
        
        for Filters in urlStringList:
            if Filters:
                url=GetRoute(url,Filters['key'],Filters['value'],request)
        
    return redirect(url)

def search_query_params_url(request,path):
    url=''
    if request.method == "POST":
        search_products = request.POST.getlist('search')
        url=f'/search_bar?'
        
        for Filters in [{"key":'products',"value":search_products},]:
            if Filters:
                url=GetRoute(url,Filters['key'],Filters['value'],request)
                
    return redirect(url)

def get_currency_instance(request):
    result = request.COOKIES.get('currency', '')
    if len(result) == 0:
        currency = Currency.objects.get(code='USD')
        return currency
    try:
        currency = Currency.objects.get(id=result)
    except ObjectDoesNotExist:
        currency = Currency.objects.get(code='USD')
        
    return currency



def convert_amount_based_on_currency(amount,request):
    currency=get_currency_instance(request)
    if currency.code == 'USD':
        return Decimal(amount)
    else:
        amount=amount/Decimal(currency.factor)
        return Decimal(amount)
    

# def random_with_N_digits(n):
#     range_start = 10**(n-1)
#     range_end = (10**n)-1
#     return randint(range_start, range_end)

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(5) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def get_product_attribute_list(id):
    product = Product.objects.get(id=id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
     # Code to seperate attribute start ==================================================
    attributeObjects = []
    attributeList = []
    attributeNameList = []
    uniqueAttributeList = []
    

    for productVariant in productVariants:
        attributes = productVariant.productVariantAttribute.all()
        for attribute in attributes:
            attributeList.append(attribute)

    uniqueAttributeList = list(set(attributeList))
    for ual in uniqueAttributeList:
        attributeNameList.append(str(ual.attributeName))

    atrList = list(set(attributeNameList))

    attributeObjectsIds=[]
    # Generate the attributeObjects based on atrList and uniqueAttributeList
    for attribute_name in atrList:
        attributeObjectsIds.append('selected'+attribute_name)
        attribute_values = []
        for attr in uniqueAttributeList:
            if str(attr.attributeName) == attribute_name:
                #attribute_values.append({'fn': attr.attributeValue, 'sn': attr.attributeValue})
                attribute_values.append(attr.attributeValue)
        attributeObjects.append({attribute_name: attribute_values})    
        
    # Code to seperate attribute end ====================================================
    
    return attributeObjects,attributeObjectsIds

def get_product_attribute_list_for_quick_view(id):
    product = Product.objects.get(id=id)
    productVariants = ProductVariant.objects.filter(variantProduct=product)
     # Code to seperate attribute start ==================================================
    attributeObjects = []
    attributeList = []
    attributeNameList = []
    uniqueAttributeList = []
    

    for productVariant in productVariants:
        attributes = productVariant.productVariantAttribute.all()
        for attribute in attributes:
            attributeList.append(attribute)

    uniqueAttributeList = list(set(attributeList))
    for ual in uniqueAttributeList:
        attributeNameList.append(str(ual.attributeName))

    atrList = list(set(attributeNameList))

    attributeObjectsIds=[]
    # Generate the attributeObjects based on atrList and uniqueAttributeList
    for attribute_name in atrList:
        attributeObjectsIds.append('selected'+attribute_name+'AtQuickView')
        attribute_values = []
        for attr in uniqueAttributeList:
            if str(attr.attributeName) == attribute_name:
                #attribute_values.append({'fn': attr.attributeValue, 'sn': attr.attributeValue})
                attribute_values.append(attr.attributeValue)
        attributeObjects.append({attribute_name: attribute_values})    
    # Code to seperate attribute end ====================================================
    
    return attributeObjects,attributeObjectsIds
