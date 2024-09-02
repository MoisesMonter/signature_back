import os
from pathlib import Path





# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Security
SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '10.0.2.2',  
    # 'fc12-200-137-2-69.ngrok-free.app',
]

#Gemini_ai
GENERATIVE_AI_API_KEY = 'AIzaSyB082qtSrAwDO0QjXOkFlYZFJYwEBMBbA0'  
GEMINI_AI_URL = "https://api.generativeai.com/v1/models/gemini-1.5-flash:generateContent" 


# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'drf_spectacular',
    'users',
    'signatures',
    'ata_model',
    'ai_tratament',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Signatures_List_Api',
    'DESCRIPTION': 'API documentation for My Project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'TAGS': [
        {'name': 'Signature Lists', 'description': 'Operations related to Signature Lists'},
        {'name': 'Signatures', 'description': 'Operations related to Signatures'},
        # Adicione outros grupos de tags conforme necessário
    ],
}
# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# URLs and WSGI
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'
CORS_ALLOW_ALL_ORIGINS = True
# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password Validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = '/static/'

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Authentication Backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Site ID
SITE_ID = 1

# Social Account Providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}
SITE_ID = 1
# Login Redirect URL
LOGIN_REDIRECT_URL = '/'
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",  
    "http://localhost:3000", 
    "http://127.0.0.1:8000",
]

from datetime import timedelta
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': False,
#     'BLACKLIST_AFTER_ROTATION': True,
#     'ALGORITHM': 'RS256',  # Clerk utiliza RS256 para assinar tokens
#     'VERIFYING_KEY': '''[{"use":"sig","kty":"RSA","kid":"ins_2kG0aL8KQP3bFLg1vhknK0RIGmB","alg":"RS256","n":"o_TB2wEgKkuxcrx-ynEOSUEdddGYe38qzzqGwDv6NcHiHepTNu-QTMaevV0KzShEzCdhTP3mtMvgEamK1LtIXQaPcR79q4an0BpKA3ByYCrqh72ixnfh2NhX94kuegD7De7N_c3hTNQOTg-YL7ASkQnEumhTYkIr1unz8VqKRs3YdHWgUJQDY1_7GhWcWJhDbvPuG3GPu5ooVYEJcxotpBkjhe07aCEowdXTSxOW9mj-QsrLWuu9V7T0_tvAS9SOZJAZlifem8ltquVP7wJzRve8UYoBD9UYtKu51cS3h-b0ZG6nM_kiDqrstvP72Kk-6w-TI0ySqA7yZtr_2CyMZQ","e":"AQAB"}]''',
# }