from django.shortcuts import redirect
from django.urls import reverse
from django.http import  HttpResponseRedirect


class RestrictUrlsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if not request.user.is_authenticated:
        #     # User is not authenticated, redirect to login page
        #     return HttpResponseRedirect(reverse('login_page'))
        
        # Check for the presence of the 'code' cookie
        code_cookie = request.COOKIES.get('code')
        
        if request.path == '/verify_token':
            if not code_cookie:
                return HttpResponseRedirect(reverse('forgot_password'))
            
        if request.path == '/update_password':
            if not code_cookie:
                return HttpResponseRedirect(reverse('forgot_password'))
        
        # checkout_cookie = request.COOKIES.get('checkout')

        # if checkout == 'False' and request.path in ['/checkout_page']:
        #     return HttpResponseRedirect(reverse('cart_page'))
        
        # if request.path == '/checkout_page':
        #     if not checkout_cookie:
        #         return HttpResponseRedirect(reverse('cart_page'))
        
        response = self.get_response(request)
        return response