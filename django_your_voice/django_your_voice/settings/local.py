from .common import *



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-(+30(rz2$l+lfbm&)oe_7s+pitlr4!-6w!86+)&1y7)9a5f@6v"



# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'your_voice',
        'USER': 'admin',
        'PASSWORD': '000000',
        'HOST': '35.236.169.31',
        'PORT': '3306',
    }
}
