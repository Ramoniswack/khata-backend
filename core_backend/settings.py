"""
Django settings for core_backend project.
"""

from pathlib import Path
from datetime import timedelta
import os
from decouple import config

# ============================================================================
# PYTHON 3.14 COMPATIBILITY PATCH
# ============================================================================
# Apply Django compatibility patch for Python 3.14
# This fixes: AttributeError: 'super' object has no attribute 'dicts'
# Remove this when upgrading to Django 5.1+ which has official Python 3.14 support
try:
    from . import django_py314_patch
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# Application definition
INSTALLED_APPS = [
    # Jazzmin must be before django.contrib.admin
    'jazzmin',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    
    # Local apps - Core
    'core_backend',
    'tenants',
    'users',
    'utils',
    
    # Local apps - Business Modules
    'inventory',
    'sales',
    'purchase',
    'suppliers',
    'accounting',
    'construction',
    'reports',
    'hr',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tenants.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'core_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core_backend.wsgi.application'

# Database
# Use SQLite for development if USE_SQLITE is True, otherwise PostgreSQL
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='khata_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Authentication Backends - Use email for login
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',  # Custom backend for email-based authentication
    'django.contrib.auth.backends.ModelBackend',  # Fallback to default
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_ACCESS_TOKEN_LIFETIME_HOURS', default=1, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')


# DRF Spectacular (Swagger/OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Khata ERP API',
    'DESCRIPTION': '''
    Multi-tenant SaaS ERP platform for Nepal.
    
    ## Authentication
    This API uses JWT (JSON Web Token) authentication. To authenticate:
    1. Register a user at `/api/auth/register/`
    2. Login at `/api/auth/login/` to get access and refresh tokens
    3. Include the access token in the Authorization header: `Bearer <token>`
    4. Refresh the token at `/api/auth/token/refresh/` when it expires
    
    ## Multi-Tenancy
    All data is automatically scoped to your tenant (organization). You can only access data 
    belonging to your organization.
    
    ## Modules
    - **Core**: Authentication, Users, Inventory, Suppliers, Accounting
    - **Construction**: Site management, labor tracking, budget monitoring
    - **Hardware**: Stock management, credit sales, customer ledger
    
    ## Currency
    All amounts are in NPR (Nepali Rupees) with paisa precision (2 decimal places).
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SERVERS': [
        {'url': 'http://127.0.0.1:8000', 'description': 'Development server'},
        {'url': 'http://localhost:8000', 'description': 'Local server'},
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and profile management'},
        {'name': 'Inventory - Categories', 'description': 'Product category management'},
        {'name': 'Inventory - Units', 'description': 'Units of measure management'},
        {'name': 'Inventory - Warehouses', 'description': 'Warehouse/storage location management'},
        {'name': 'Inventory - Products', 'description': 'Product management and stock tracking'},
        {'name': 'Inventory - Stocks', 'description': 'Stock level monitoring'},
        {'name': 'Inventory - Movements', 'description': 'Stock movement history'},
        {'name': 'Inventory - Operations', 'description': 'Stock operations (in/out/transfer/adjustment)'},
        {'name': 'Sales - Customers', 'description': 'Customer management'},
        {'name': 'Sales - Orders', 'description': 'Sales order management'},
        {'name': 'Sales - Quotations', 'description': 'Quotation management'},
        {'name': 'Sales - Invoices', 'description': 'Invoice management'},
        {'name': 'Sales - Credit Notes', 'description': 'Credit note management'},
        {'name': 'Purchase - Suppliers', 'description': 'Supplier management'},
        {'name': 'Purchase - Requests', 'description': 'Purchase request management with 3-step approval'},
        {'name': 'Purchase - Orders', 'description': 'Purchase order management'},
        {'name': 'Purchase - Invoices', 'description': 'Purchase invoice management'},
        {'name': 'Purchase - Debit Notes', 'description': 'Debit note management'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    'SECURITY': [
        {
            'bearerAuth': []
        }
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}




# ============================================================================
# JAZZMIN ADMIN THEME - Clean & Minimal Configuration
# ============================================================================

JAZZMIN_SETTINGS = {
    # Site branding
    "site_title": "KHATA Admin",
    "site_header": "KHATA",
    "site_brand": "KHATA Business OS",
    "site_logo": None,
    "site_icon": None,
    "welcome_sign": "Welcome to KHATA Business OS",
    "copyright": "KHATA © 2026",
    
    # Search
    "search_model": ["users.User", "tenants.Tenant", "inventory.Product", "sales.Customer"],
    
    # Top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
    ],
    
    # User menu
    "usermenu_links": [
        {"model": "users.user"}
    ],
    
    # Side menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # App ordering
    "order_with_respect_to": [
        "tenants",
        "users",
        "inventory",
        "sales",
        "purchase",
        "accounting",
        "construction",
        "hr",
        "reports",
    ],
    
    # Icons for models
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user-tie",
        "tenants.Tenant": "fas fa-building",
        
        "inventory.Product": "fas fa-box",
        "inventory.Category": "fas fa-tags",
        "inventory.Warehouse": "fas fa-warehouse",
        "inventory.UnitOfMeasure": "fas fa-ruler",
        
        "sales.Customer": "fas fa-user-friends",
        "sales.SalesOrder": "fas fa-shopping-cart",
        "sales.Quotation": "fas fa-file-invoice",
        "sales.Invoice": "fas fa-file-invoice-dollar",
        
        "purchase.Supplier": "fas fa-truck",
        "purchase.PurchaseOrder": "fas fa-shopping-bag",
        "purchase.PurchaseRequest": "fas fa-clipboard-list",
        
        "accounting.Account": "fas fa-chart-pie",
        "accounting.JournalEntry": "fas fa-book-open",
        "accounting.BankAccount": "fas fa-university",
        
        "construction.Site": "fas fa-hard-hat",
        "construction.Worker": "fas fa-user-hard-hat",
        "construction.Equipment": "fas fa-tractor",
        
        "hr.Employee": "fas fa-id-card",
        "hr.Department": "fas fa-sitemap",
        "hr.Attendance": "fas fa-calendar-check",
        "hr.Payroll": "fas fa-money-bill-wave",
    },
    
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # UI Tweaks
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Change form format
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "horizontal_tabs",
        "users.user": "horizontal_tabs",
    },
    
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-white",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}
