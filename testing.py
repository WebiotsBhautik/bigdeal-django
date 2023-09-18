#  <div class="detail-right">
# <div class="check-price">
# {% if product.productType == "Simple" %} 
# {{""|return_currency_wise_symbol:request}}{{product.product_actual_price_range|return_currency_wise_ammount:request}} 
# {% else %} 
# {{product.product_actual_price_range|return_currency_wise_ammount_range:request}}
# {% endif %}
# </div>
# <div class="price">
# <div class="price">
#     {% if product.productType == "Simple" %}
#     {{""|return_currency_wise_symbol:request}}{{product.product_price_range|return_currency_wise_ammount:request}}
#     {% else %}
#     {{product.product_price_range|return_currency_wise_ammount_range:request}}
#     {% endif %}
# </div>
# </div>
# </div>




#  <h2>{% if banner.bannerProduct.productVariantDiscount|to_int == 0 %}
# {% else %}
# <span class="theme-color">{{banner.bannerProduct.productVariantDiscount}}% OFF</span>
# {% endif %} on all selected product</h2>



# <span class="detail-price">
#                                     {% if product.productType == "Simple" %}
#                                     {{""|return_currency_wise_symbol:request}}{{product.product_price_range|return_currency_wise_ammount:request}}
#                                     {% else %}
#                                     {{product.product_price_range|return_currency_wise_ammount_range:request}}
#                                     {% endif %}
#                                     <del>
#                                        {% if product.productType == "Simple" %} 
#                                        {{""|return_currency_wise_symbol:request}}{{product.product_actual_price_range|return_currency_wise_ammount:request}} 
#                                        {% else %} 
#                                        {{product.product_actual_price_range|return_currency_wise_ammount_range:request}}
#                                        {% endif %}
#                                     </del>
#                                  </span>



# def quick_view(request):
#     if request.method == 'POST':
#         body = json.loads(request.body)

#         productId = body["productId"]
#         productVariantId = body["productVariantId"]

#         product = Product.objects.get(id=productId)
#         productVariant = ProductVariant.objects.get(id=productVariantId)
#         firstProductVariant = ProductVariant.objects.filter(variantProduct=product).first()
#         multipleImages = MultipleImages.objects.filter(multipleImageOfProduct=product)
#         multipleImgList = []

#         for image in multipleImages:
#             multipleImgList.append(str(image.multipleImages.url))

#         singleImage=str(productVariant.variantProduct.productImageFront)

#         attributeObjects, attributeObjectsIds = get_product_attribute_list_for_quick_view(product.id)
        
#         if product.productType == "Simple":
#             productVariantMinPrice = None
#             productVariantMaxPrice = None
#             productVariantMinActualPrice = None
#             productVariantMaxActualPrice = None
#             productVariantActualPrice = product.product_actual_price_range
#             productVariantDiscountRange = None
#             productVariantDiscount = product.product_discount_range
#             productVariantPrice1 = product.product_price_range

#         if product.productType == "Classified":
#             productVariantMinPrice = product.product_price_range[0]
#             productVariantMaxPrice = product.product_price_range[1]
#             productVariantMinActualPrice = product.product_actual_price_range[0]
#             productVariantActualPrice = None
#             productVariantMaxActualPrice = product.product_actual_price_range[1]
#             productVariantDiscountRange = product.product_discount_range
#             productVariantDiscount = None
#             productVariantPrice1 = None
       
        
#         data = {
#             "productId": product.id,
#             "firstProductVariant": firstProductVariant.id,
#             "productVariantId": productVariant.id,
#             "productName": productVariant.variantProduct.productName,
#             "productFinalRating": product.productFinalRating,
#             "productStockStatus": productVariant.productVariantStockStatus,
#             "productVariantPrice1": productVariantPrice1,
            
#             "productVariantMinPrice": productVariantMinPrice,
#             "productVariantMaxPrice": productVariantMaxPrice,
        
#             "productVariantMinActualPrice" : productVariantMinActualPrice,
#             "productVariantMaxActualPrice" : productVariantMaxActualPrice,
#             "productVariantDiscountRange" : productVariantDiscountRange,
            
#             "productVariantActualPrice":productVariantActualPrice,
#             "productVariantDiscount":productVariantDiscount,
            
#             "productImageFront": str(product.productImageFront),
#             "multipleImages": multipleImgList,
#             "singleImage":singleImage,

#             "productType": product.productType,

#             "attributeObjects":attributeObjects,
#             "attributeObjectsIds":attributeObjectsIds,

#             "brand": str(product.productBrand),
#             "category": str(product.proCategory)
#         }

#         return JsonResponse(data, safe=False)










