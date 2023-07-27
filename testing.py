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




# # start:stop:step
# name =[ 'vishal' , 'bhautik' , 'keyur','raj']
# # name.append('urvish')
# print(name[1:3])





# {% load static %}
# {% load sass_tags %}
# {% load custom_templatetags %}
# {% load mathfilters %}

# <!-- Offcanvas Section Start -->
#     <form action="{% url 'create_query_params_url' path %}" method="post">
#         {% csrf_token %}
#         {% for name,values in attributeDict.items %}
#         <div class="accordion-item category-price">
#             <h2 class="accordion-header" id="headingFive">
#                 <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFive{{ forloop.counter }}">
#                     {{name}}
#                 </button>
#             </h2>
            
#             <div  class="accordion-collapse collapse show" id="collapseFive{{ forloop.counter }}"
#                 aria-labelledby="headingFive" data-bs-parent="#accordionExample" >
#                 <div class="accordion-body">
#                     <ul class="category-list">
#                         {% for value in values %}
#                         <li>
#                             <div class="form-check ps-0 custome-form-check">
#                                 <input class="checkbox_animated check-it" type="checkbox" id="{{value}}{{name}}CheckBox" name="{{name}}" value="{{value}}" {% if value in request.GET.selectedAttribute|return_selected_attribute_list:request %} checked  {% endif %}>
#                                 <label class="form-check-label" for="flexCheckDefault">{{value}}</label>
#                             </div>
#                         </li>
#                         <br>
#                         {% endfor %}
#                     </ul>
#                 </div>
#             </div>
#         </div>
#         {% endfor %}
        
#         <!-- Brand Section Start -->

#             <div class="accordion-item category-rating">
#                 <h2 class="accordion-header" id="headingTwo">
#                     {% include 'includes/alerts.html' %}
#                     <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">
#                         Brand
#                     </button>
#                 </h2>

#                 <div id="collapseTwo" class="accordion-collapse collapse show" data-bs-parent="#accordionExample">
#                     <div class="accordion-body category-scroll brand">
#                         <ul class="category-list">
#                             {% for brand in ProductsBrand %}
#                             <li>
#                                 <div class="form-check ps-0 custome-form-check">
#                                     <input class="checkbox_animated check-it" type="checkbox"
#                                         name="allbrand"  value="{{brand.brandName}}" id="{{brand.brandName}}brandsCheckBox" {% if brand.brandName in request.GET.brands %} checked {% endif %}>
#                                     <label class="form-check-label brand"  for="flexCheckDefault1">{{brand.brandName}}</label>
#                                     <p class="font-light">({{brand.brandTotalProduct}})</p>
#                                 </div>
#                             </li>
#                             {% empty %}    
#                             <h2> No data Found</h2>
#                             {% endfor %}
#                         </ul>
#                     </div>
#                 </div>
#             </div>
#         <!-- Brand Section End -->

#         <!-- Price Section Start -->

#             <div class="accordion-item category-price">
#                 <h2 class="accordion-header" id="headingFour">
#                     <button class="accordion-button" type="button" data-bs-toggle="collapse"
#                         data-bs-target="#collapseFour">
#                         Price
#                     </button>
#                 </h2>
#                 <div id="collapseFour" class="accordion-collapse collapse show" aria-labelledby="headingFour"
#                     data-bs-parent="#accordionExample">
#                     <div class="accordion-body">
#                         <div class="range-slider category-list">
#                             <input type="text" min="{{min_price}}" max="{{max_price}}" prefix="{{symbol}}" name="pricefilter" data-filter="price" id="filter-price-range"  class="js-range-slider" value="" />
#                         </div>
#                     </div>  
#                 </div>  
#             </div>
#         <!-- Price Section End -->


#         <!-- Rating Section Start -->

#             <div class="accordion-item category-rating">
#                 <h2 class="accordion-header" id="headingOne">
#                     <button class="accordion-button" type="button" data-bs-toggle="collapse"
#                         data-bs-target="#collapseOne">
#                         Ratings
#                     </button>
#                 </h2>
#                 <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne">
#                     <div class="accordion-body">
#                         <ul class="category-list">
#                             {% for rating in rating_range %}
#                             <li>  
#                                 <div class="form-check ps-0 custome-form-check">
#                                     <input class="checkbox_animated check-it" type="radio" id="{{rating}}ratingsCheckBox" name="ratings" value="{{rating}}"  {% if rating in request.GET.ratings %} checked {% endif %}>
#                                     <ul class="rating mt-0">
#                                         {% for i in rating_range %}
#                                             {% if i <= rating %}
#                                                 <li class="rating-list">
#                                                     <i class="fas fa-star theme-color"></i>
#                                                 </li>  
#                                             {% else %}
#                                                 <li class="rating-list">
#                                                     <i class="fas fa-star"></i>
#                                                 </li>  
#                                             {% endif %}
#                                         {% endfor %}
#                                     </ul>
#                                     <p class="font-light"></p>
#                                 </div>
#                             </li>
#                             {% endfor %}
#                         </ul>
#                     </div>
#                 </div>
#             </div>

#         <!-- Rating Section End -->


#         <!-- Discount Section Start -->

#             <div class="accordion-item">
#                 <h2 class="accordion-header" id="headingFive">
#                     <button class="accordion-button" type="button" data-bs-toggle="collapse"
#                         data-bs-target="#collapseFive">
#                         Discount Range
#                     </button>
#                 </h2>
#                 <div id="collapseFive" class="accordion-collapse collapse show" aria-labelledby="headingFive"
#                     data-bs-parent="#accordionExample">
#                     <div class="accordion-body">
#                         <ul class="category-list">
#                         {% for discount_filter in discount_filters %}
#                             <li>
#                                 <div class="form-check ps-0 custome-form-check">
#                                     <input class="checkbox_animated check-it" type="radio"
#                                     id="{{discount_filter.value}}discountCheckBox" name="discount" value="{{discount_filter.value}}"  {% if discount_filter.value in request.GET.discount %} checked  {% endif %}>
#                                     <label class="form-check-label" for="flexCheckDefault">{{discount_filter.title}}</label>
#                                 </div>
#                             </li>
#                         {% endfor %}
#                         </ul>
#                     </div>
#                 </div>
#             </div>


#         <!-- Discount Section End -->

#             <div class="accordion-button sumbit-button">
#                 <button type="submit"  class="btn btn-solid-default" id="submitBtnAtFilterSidebar">Submit</button>   
#             </div>
#     </form>
# <!-- Offcanvas Section End -->









#  ========>  CANVAS-FILTER <==========






# def canvas_filter(request, category_id=None):
#     url = ''
#     discount_filters = [{"title": "5% and above", "value": str(5)}, {"title": "10% and above", "value": str(10)}, {"title": "20% and above", "value": str(20)}]
# #     # size_filters = [{"title": 'S', "value": "S"}, {"title": 'M', "value": 'M'}, {"title": 'L', "value": 'L'}, {"title": 'XL', "value": 'XL'}, {"title": 'XXL', "value": 'XXL'}, {"title": 'XXXL', "value": 'XXXL'}]

#     selected_allbrand = request.GET['brands'] if 'brands' in request.GET else []
#     selected_allprice = request.GET['price'] if 'price' in request.GET else []
#     selected_alldiscount = request.GET['discount'] if 'discount' in request.GET else []
#     selected_rating = request.GET['ratings'] if 'ratings' in request.GET else []

    
#     attributeNameList=[]
#     attributeDictionary={}
#     attributeName = AttributeName.objects.all()
#     for attribute in attributeName:
#         attributeNameList.append(attribute.attributeName)
        
#     for attribute in attributeNameList:
#         attributeDictionary[attribute] = request.GET[attribute] if attribute in request.GET else []

#     brand = ProBrand.objects.all()
#     category = ProCategory.objects.all()
#     product = ProductVariant.objects.all()
#     shop_bnr = BannerType.objects.get(bannerTypeName='Shop Banner')
#     shop_banner = Banner.objects.filter(bannerType=shop_bnr).first()
#     rating_range = ['1', '2', '3', '4', '5']
#     categoryid = ()

#     if category_id:
#         categoryid = ProCategory.objects.get(id=category_id)
#         product = ProductVariant.objects.filter(
#             variantProduct__proCategory=categoryid)

#         brandList = []
#         brand = []

#         for p in product:
#             brandList.append(str(p.variantProduct.productBrand.brandName))

#         for b in list(set(brandList)):
#             brand.append(ProBrand.objects.get(brandName=b))
#         url = reverse('canvas_filter_with_id', args=[id])
        


#     if selected_allprice:
#         price = selected_allprice.split(',')

#         price_filter = product
#         # product = price_filter.filter(productVariantFinalPrice__range=(price[0], price[1]))
#         current_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
#         factor = current_currency.factor

#         # print('current_currency ===========+>',current_currency.factor,type(current_currency.factor))
#         product = price_filter.filter(productVariantFinalPrice__range=(Decimal(price[0])/factor, Decimal(price[1])/factor))
#         # print('product =======+>',product)
#         # print('price[0] =======+>',price[0],price[1])
#         # print('FACTOR =======+>',int(price[0])/current_currency.factor, int(price[0])/current_currency.factor)
        

#     if selected_rating:
#         rating = selected_rating.rstrip(',')
#         rating_filter = product
#         if len(rating_filter):
#             product = rating_filter.filter(
#                 variantProduct__productFinalRating=rating)
            
            

#     if selected_allbrand:
#         brand_filter = product
#         x = selected_allbrand.split(',')
#         y = x[:-1]
#         product = []
#         for brands in y:
#             product1 = brand_filter.filter(variantProduct__productBrand__brandName=brands)
#             product += product1

#     if selected_alldiscount:
#         x = selected_alldiscount.split(',')
#         select_disc = x[:-1]
#         discount_filter = product

#         if len(discount_filter) and type(discount_filter) is not list:
#             product = discount_filter.filter(productVariantDiscount__gte=select_disc[0])
#         else:
#             sbd = request.GET['brands'] if 'brands' in request.GET else []
#             x = sbd.split(",")
#             y = x[:-1]
#             brands = [s.strip('"') for s in y]
#             product = ProductVariant.objects.filter(variantProduct__productBrand__brandName__in=brands)
    
#     if attributeDictionary:
#         for attribute in attributeNameList:
#             if attributeDictionary[attribute]:
#                 if type(product) is not list:
#                     attribute_filter = product
#                 else:
#                     productIdList = [p.id for p in product]  
#                     attribute_filter = ProductVariant.objects.filter(id__in=productIdList)
#                 x = attributeDictionary[attribute].split(',')
#                 y = x[:-1]
#                 product = []
#                 for values in y:
#                     attributeNameObj=AttributeName.objects.get(attributeName=attribute)
#                     product1 = attribute_filter.filter(productVariantAttribute__attributeName=attributeNameObj,productVariantAttribute__attributeValue=values)
#                     product += product1
     

#     attributeDict = {}
#     attributeName = AttributeName.objects.all()
#     for attribute in attributeName:
#         attributeDict[attribute.attributeName]=[]
#         attributeValue = AttributeValue.objects.filter(attributeName=attribute)
#         for value in attributeValue:
#             attributeDict[attribute.attributeName].append(value.attributeValue)
            
#     product = GetUniqueProducts(product)
#     paginator = Paginator(product,5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     # min_price_combined = f"{selected_currency.symbol} {min_price * selected_currency.factor}" 
#     totalProduct = len(product)
    
#     get_all_prices = ProductVariant.objects.values_list('productVariantFinalPrice', flat=True)
#     min_price = []
#     max_price = []
#     print('get_all_prices ============>',get_all_prices)
#     if get_all_prices:
#         min_price = min(list(get_all_prices))
#         max_price = max(list(get_all_prices))
        
#     print('BEFORE min_price ========>',min_price)
    
#     selected_currency = Currency.objects.get(id=request.COOKIES.get('currency', ''))
#     if product and selected_currency:
#         min_price = min_price*selected_currency.factor
#         max_price = max_price*selected_currency.factor
        
#     print('AFTER min_price ========>',min_price)
    
#     print('min_price =========++>',min_price)
#     print('max_price =============+>',max_price)


#     context = {"breadcrumb": {"parent": "Shop Canvas Filter", "child": "Shop Canvas Filter"},
#             'products': product, 'ProductsBrand': brand, 'ProductCategory': category,
#             'productVariant':product,
#             'shop_banner':shop_banner,
#             'categoryid':categoryid,
#             'url':url,
#             'rating_range':rating_range,
#             'discount_filters':discount_filters,
#             'select_brands':selected_allbrand,
#             'selected_prices':selected_allprice,
#             'selected_discounts':selected_alldiscount,
#             'path':'canvas_filter',
#             'page_obj':page_obj,
#             'attributeDict':attributeDict,
#             'min_price':min_price,
#             'max_price':max_price,
#             'symbol':selected_currency.symbol,
#             'totalProduct':totalProduct,
#             # 'min_price':min_price*selected_currency.factor,
#             # 'max_price':max_price*selected_currency.factor,
#             }
    
#     return render(request,'pages/shop/canvas-filter.html', context)



