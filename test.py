# def search_bar(request, params=None):
#     query = ''
#     data = ''
#     products = ProductVariant.objects.all()
#     if 'search' in request.GET:
#         query = request.GET.get('search')

#         if query:
#             if params:
#                 products = ProductVariant.objects.filter(
#                     variantProduct__productName__icontains=query)
#                 data = [{'id': p.variantProduct.id, 'name': p.variantProduct.productName, 'category': p.variantProduct.proCategory.categoryName,
#                          'brand': p.variantProduct.productBrand.brandName, 'description': p.variantProduct.productDescription, } for p in products]
#             else:
#                 products = ProductVariant.objects.all()

#     products = GetUniqueProducts(products)
#     paginator = Paginator(products,8)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    

#     context = {"breadcrumb": {"parent": "Search", "child": "Search"}, 'products': products,
#                'query': query,'page_obj':page_obj, }
    
#     return render(request, 'pages/pages/search.html', context)


# def forgot_password(request):
#     active_banner_themes = BannerTheme.objects.filter(is_active=True)
#     if request.method == 'POST':
#         email = request.POST['emailname']
#         if CustomUser.objects.filter(email=email).exists():
#             user = CustomUser.objects.get(email__exact=email)
#             current_site = get_current_site(request)
#             mail_subject = 'Reset Your Password'
#             otp = generateOTP()
#             message = render_to_string('authentication/reset_password_email.html', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token': otp,
#             })
#             to_email = email
#             mail = EmailMultiAlternatives(mail_subject, message, to=[to_email])
#             mail.attach_alternative(message, "text/html")
#             mail.send()
#             temDataObject = TemporaryData.objects.get(
#                 TemporaryDataByUser__email=email)
#             temDataObject.otpNumber = otp

#             current_time = datetime.now()
#             temDataObject.otpExpiryTime = current_time + timedelta(minutes=1)
#             temDataObject.save(update_fields=['otpNumber', 'otpExpiryTime'])

#             response = HttpResponseRedirect('verify_token')
#             response.set_cookie('code', user.id, max_age=180)
#             messages.success(
#                 request, 'An OTP has been sent to your email address successfully')
#             return response
#         else:
#             messages.error(request, 'Account Does Not Exist!')
#             return redirect('forgot_password')
#     return render(request, 'authentication/forgot.html',{'active_banner_themes':active_banner_themes})




# def verify_token(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         get_id = request.COOKIES['code']
#         get_user = CustomUser.objects.get(id=get_id)

#         temDataObject=TemporaryData.objects.get(TemporaryDataByUser=get_user)
#         stored_otp = temDataObject.otpNumber
#         current_time = timezone.now()
#         exp_time = temDataObject.otpExpiryTime

#         if current_time < exp_time:
#             if entered_otp == stored_otp:
#                 print(' =====. OTP MATCH <============')
#                 messages.success(request, 'OTP Verified')
#                 return redirect('update_password')
#             else:
#                 print('=====> OTP DOES NOT MATCH <========')
#                 messages.error(request, 'Invalid OTP. Please try again.')
#                 return redirect('verify_token')
#         else:
#             messages.error(
#                 request, 'Your otp has been expired! Please regenerate otp.')
#             return redirect('forgot_password')
#     return render(request, 'authentication/verify_token.html')




# def update_password(request):
#     if request.method == 'POST':
#         password = request.POST['newpass']
#         conf_password = request.POST['confnewpass']

#         password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
#         user = CustomUser.objects.get(username__exact=request.user.username)
#         if password and conf_password:
#             if not re.search(password_pattern, password):
#                 messages.warning(
#                     request, 'Password must be at least 8 characters long and contain at least one letter and one number')
#                 return redirect('update_password')

#             if password == conf_password:
#                 user.set_password(password)
#                 user.save()
#                 messages.success(request, 'Password updated successfully')
#                 return redirect('login_page')
#             else:
#                 messages.error(request, 'Password Does Not Match')
#                 return redirect('update_password')
#     return render(request, 'authentication/update_password.html')



# def change_password(request):
#     if request.method == 'POST':
#         current_password = request.POST['currentpass']
#         new_password = request.POST['newpass']
#         confirm_password = request.POST['confnewpass']

#         user = CustomUser.objects.get(username__exact=request.user.username)
#         if new_password == confirm_password:
#             success = user.check_password(current_password)
#             if success:
#                 user.set_password(new_password)
#                 user.save()
#                 messages.success(request, 'Password changed successfully')
#                 return redirect('login_page')
#             else:
#                 messages.error(request, 'Please enter valid current password')
#                 return redirect('change_password')
#         else:
#             messages.error(request, 'Password Does Not Match')
#             return redirect('change_password')
#     else:
#         return render(request, 'authentication/change_password.html')





# def contact_us(request):
#     active_banner_themes = BannerTheme.objects.filter(is_active=True)
#     if request.method == 'POST':
#         firstname = request.POST['first']
#         lastname = request.POST['last']
#         email = request.POST['email']
#         confirm_email = request.POST['email2']
#         number = request.POST['number']
#         comment = request.POST['comment']
#         name=str(firstname)+" "+str(lastname)

#         if ContactUs.objects.filter(contactUsEmail=email).exists():
#             messages.warning(request, 'Email already exists')
#         else:
#             if email == confirm_email:
#                 user = ContactUs.objects.create(contactUsName=name, contactUsEmail=email,contactUsNumber=number ,contactUsComment=comment)
#                 user.save()
#                 messages.success(request, 'Your form has been submitted successfully')
#                 return redirect('contact_us')
#             else:
#                 messages.error(request, 'Email Does Not Match')
#                 return redirect('contact_us')
#         return render(request, 'pages/pages/contact-us.html')
#     else:
#         context = {"breadcrumb": {"parent": "Contact Us", "child": "Contact Us"},
#                    'active_banner_themes':active_banner_themes,
#                 }
#         return render(request, 'pages/pages/contact-us.html', context)



# def search_products(request):
#     query = request.GET.get('q','')
#     category = request.GET.get('category', '') 
   
#     products = ProductVariant.objects.all()
   
#     if query and category:
#         fashion_subcategories = get_subcategories(category)
#         category_ids = []
#         category_ids.extend(get_category_ids(fashion_subcategories))
#         products = products.filter(variantProduct__proCategory__id__in=category_ids, variantProduct__productName__icontains=query)
#     else:
#         fashion_subcategories = get_subcategories(category)
#         category_ids = []
#         category_ids.extend(get_category_ids(fashion_subcategories))
#         products = ProductVariant.objects.filter(variantProduct__proCategory__id__in=category_ids).order_by('id')[:7]

          
#     products = GetUniqueProducts(products)
#     results = [{'id': product.variantProduct.id,
#                 'name': product.variantProduct.productName,
#                 'price': product.productVariantFinalPrice, 
#                 'image_url': product.variantProduct.productImageFront.url if product.variantProduct.productImageFront else '',
#                 'rating': product.variantProduct.productFinalRating,
#                 'category': product.variantProduct.proCategory.categoryName  
#                 } for product in products]
    
#     return JsonResponse({'status': 200, 'data': results})







