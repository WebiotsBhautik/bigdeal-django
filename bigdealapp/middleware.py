from django.shortcuts import redirect,render
from django.urls import reverse
from django.http import  HttpResponseRedirect
from bigdealapp.views import show_cart_popup


class RestrictUrlsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        if response.status_code == 404:
            cart_products,totalCartProducts = show_cart_popup(request)
            context = {"breadcrumb": {"parent": 404, "child": 404},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
            return render(request, 'pages/pages/404.html',context)
        return response