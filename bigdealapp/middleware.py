from django.shortcuts import redirect,render
from django.urls import reverse
from django.http import  HttpResponseRedirect
from bigdealapp.views import show_cart_popup
from django.contrib import messages


class RestrictUrlsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and 'code' not in request.COOKIES and request.path in ['/verify_token','/update_password']:
            return HttpResponseRedirect(reverse('login_page'))
        
        checkout = request.COOKIES.get('checkout')

        if checkout == 'False' and request.path in ['/checkout_page']:
            return HttpResponseRedirect(reverse('cart_page'))
        
        if 'checkout' not in request.COOKIES and request.path in ['/checkout_page']:
            return HttpResponseRedirect(reverse('cart_page'))
        
        response = self.get_response(request)
        if response.status_code == 404:
            cart_products,totalCartProducts = show_cart_popup(request)
            context = {"breadcrumb": {"parent": 404, "child": 404},
               "cart_products": cart_products, "totalCartProducts": totalCartProducts,}
            return render(request, 'pages/pages/404.html',context)
        
        return response
    
    
class RestrictDatabaseAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.method == 'POST':
                if not self.is_login_request(request):
                    messages.error(request, 'This Section Does Not Allowed In demo Mode')
                    return HttpResponseRedirect('/admin/')
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                messages.error(request, 'This Section Does Not Allowed In demo Mode')
                return HttpResponseRedirect('/admin/')
        return self.get_response(request)
    
    def is_login_request(self, request):
        if request.path.startswith('/signup_page') and request.method == 'POST':
            return True
        return request.path.startswith('/login_page') or request.path == '/admin/login/' 