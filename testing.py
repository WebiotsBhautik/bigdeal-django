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



