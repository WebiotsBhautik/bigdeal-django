"""
Django settings for bigdeal project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import mimetypes
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sq-%-(rvn6qkp0bv7vbbro=+0-q2v!y1l^$w6cs@4s62%jv4)='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',
    'ckeditor',
    'mptt',
    'bigdealapp',
    'accounts',
    'product',
    'order',
    'payment',
    'mathfilters',
    'currency',
    'shell_plus',
    'django_extensions',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.get_username.RequestMiddleware',
    'bigdealapp.middleware.RestrictUrlsMiddleware',
    # 'bigdealapp.middleware.RestrictDatabaseAccessMiddleware',  
]

ROOT_URLCONF = 'bigdeal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'bigdealapp/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {    
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bigdeal.context_processors.dashboardData',
            ],
        },
    },
]

WSGI_APPLICATION = 'bigdeal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'mydatabase',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]


STATIC_URL = '/bigdeal/bigdealapp/static/'

STATIC_ROOT = BASE_DIR / 'bigdealapp/static'

SASS_PROCESSOR_ROOT = BASE_DIR / 'bigdealapp/static'

MEDIA_ROOT = BASE_DIR / 'bigdealapp/static/assets/images'



# Rozarpay settings ===================================================
RAZORPAY_KEY_ID = 'rzp_test_iV7SM01Wb7wvhv'
RAZORPAY_SECRET_KEY = 'gjdchqP3v7shiW7SRKo2xecV'

# =====================================================================

# PayPal settings ===================================================
# PAYPAL_CLIENT_ID = 'ATWp1z5IroqlimLbKru4uwqcniWEVAjNbN5OBn4A20wBNCEKZiT2Sc0Ywc55plhZZvpyskMqLUGz-Bca'
# =====================================================================

PAYPAL_CLIENT_ID = 'AWSvIg3u2s-p7g2RYkcktJLjtn3Rsw0LZAm0CoS6WeYtEoYmSzRC01bT0wVxz4whG3eN4bCu1vparBbp'

PAYPAL_SECRET = 'EPtAGaQiNig5iYMuxtoFs_kVimBODw7axl7hSjn21YLPi6aCRJymPoU2n9GtLWNVqXGWj155XRK7Kpcm'



# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

MPTT_ADMIN_LEVEL_INDENT = 20

X_FRAME_OPTIONS = 'SAMEORIGIN'

JAZZMIN_SETTINGS = {
    "custom_css": "assets/css/backend.css",
    "custom_js": "assets/js/custom.js",
    
    "use_google_fonts_cdn": False,
    "site_logo": "assets/images/logos/logo.png",
    "favicon_icon": "assets/images/favicon/favicon.png",
    "welcome_sign": "Welcome to Bigdeal Ecommerce",
    "copyright": "Bigdeal theme by pixelstrap",
    # "language_chooser": True,
    "icons": {
        # Icon's for Account
        "accounts.CustomUser": "fas fa-user",
        "accounts.Admin": "fas fa-user",
        "accounts.Vendor": "fas fa-user",
        
        "product.Product": "fas fa-box",
        "product.ProductVariant": "fas fa-cube",
        "product.AttributeName": "fas fa-tasks",
        "product.ProCategory": "fas fa-stream",
        "product.ProBrand": "fas fa-gem",
        "product.ProUnit": "fas fa-archive",
        "product.ProVideoProvider": "fas fa-video",
        "product.ProductReview": "fas fa-star",
        "product.MultipleImages": "fas fa-image",

        "order.Order": "fas fa-boxes",
        "order.ProductOrder": "fas fa-box",
        "order.OrderPayment": "fas fa-money-bill-wave-alt",
        "order.OrderTracking": "fas fa-truck",
        "order.Cart": "fas fa-shopping-cart",
        "order.Wishlist": "fas fa-heart",
        "order.Compare": "fas fa-sync-alt",
        "order.CartProducts": "fas fa-cart-plus",
        "order.OrderBillingAddress": "fas fa-address-card",
        "order.PaymentMethod": "fas fa-credit-card",

        "payment.Card": "fab fa-cc-visa",
        "payment.Wallet":"fas fa-wallet",
        "payment.WalletHistory":"fas fa-history",
        "payment.Withdrawal":"fas fa-money-check-alt",

        "currency.Currency": "fas fa-dollar-sign",

        "bigdealapp.BannerTheme": "fas fa-palette",
        "bigdealapp.BannerType": "fas fa-image",
        "bigdealapp.Banner": "fas fa-image",
        "bigdealapp.BlogCategory": "fas fa-clipboard-list",
        "bigdealapp.Blog": "fas fa-blog",
        "bigdealapp.BlogComment": "fas fa-comment-dots",
        "bigdealapp.Coupon": "fas fa-ticket-alt",
        "bigdealapp.CouponHistory": "fas fa-history",
        "bigdealapp.ContactUs": "fas fa-phone-square",
        # "bigdealapp.TodoTask":"fas fa-list-ul",

        "logout": "fas fa-sign-out-alt",
        "auth.Group": "fas fa-users",
    },

    "changeform_format": "vertical_tabs",
    "related_modal_active": True,
    "topmenu_links": [],
    "usermenu_links": [],
    
    # Keep the same app ordering as above, but also order choice and book model links within the books app
    "order_with_respect_to": [
        # APPLICATIONS Orderings
        "accounts", "auth", "product", "order", "payment", "currency", "bigdealapp",
    
    
    # Models Ordering for ACCOUNT Application
    "accounts.CustomUser", "accounts.Admin", "accounts.Vendor", "accounts.Customer",

    # Models Ordering for PRODUCT Application
    "product.Product", "product.ProductVariant", "product.AttributeName", "product.ProCategory",
    "product.ProBrand", "product.ProUnit", "product.ProVideoProvider", "product.ProductReview",
    
    # Models Ordering for ORDER Application
    "order.Order", "order.ProductOrder", "order.OrderPayment", "order.OrderTracking", "order.Cart",
    "order.Wishlist", "order.Compare", "order.CartProducts", "order.OrderBillingAddress", "order.PaymentMethod",
    
    # Models Ordering for CURRENCY Application
    "payment.Wallet", "payment.WalletHistory",

    # Models Ordering for CURRENCY Application
    "currency.Currency",
    
    # Models Ordering for BIGDEALAPP Application
    "bigdealapp.BannerTheme", "bigdealapp.BannerType", "bigdealapp.Banner",
    "bigdealapp.BlogCategory", "bigdealapp.Blog", "bigdealapp.BlogComment",
    "bigdealapp.Coupon", "bigdealapp.CouponHistory","bigdealapp.ContactUs"
    ],
}

# JAZZMIN_UI_TWEAKS = {
#     "theme": "darkly",
# }
 
 
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}   


# SMTP Configurations
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'webapp342@gmail.com'
EMAIL_HOST_PASSWORD = 'uspgrohipaiawirb'
EMAIL_PORT = 587
