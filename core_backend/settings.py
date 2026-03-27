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
# JAZZMIN SETTINGS - Premium SaaS Admin Interface
# ============================================================================

JAZZMIN_SETTINGS = {
    # Site branding
    "site_title": "KHATA Admin",
    "site_header": "KHATA",
    "site_brand": "KHATA Business OS",
    "site_logo": None,  # Path to logo image in static files
    "site_logo_classes": "img-circle",
    "site_icon": None,  # Favicon path
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Khata Business OS",
    
    # Copyright on the footer
    "copyright": "Khata ERP © 2026 | Professional Business Management System",
    
    # Search model in the sidebar
    "search_model": ["auth.User", "tenants.Tenant", "inventory.Product", "sales.Customer", "purchase.Supplier"],
    
    # Field name on user model that contains avatar
    "user_avatar": None,
    
    ############
    # Top Menu #
    ############
    
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        
        # External url
        {"name": "API Documentation", "url": "/api/docs/", "new_window": True},
        
        # Model admin to link to (Permissions checked against model)
        {"model": "auth.User"},
        
        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "inventory"},
    ],
    
    #############
    # User Menu #
    #############
    
    # Additional links to include in the user menu on the top right
    "usermenu_links": [
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
        {"model": "auth.user"},
    ],
    
    #############
    # Side Menu #
    #############
    
    # Whether to display the side menu
    "show_sidebar": True,
    
    # Whether to auto expand the menu
    "navigation_expanded": True,
    
    # Hide these apps when generating side menu
    "hide_apps": [],
    
    # Hide these models when generating side menu (e.g. 'auth.group')
    "hide_models": ["auth.Group"],  # Hide unused models for cleaner UI
    
    # List of apps (and/or models) to base side menu ordering off of
    "order_with_respect_to": [
        "tenants",
        "users",
        "inventory",
        "sales",
        "purchase",
        "accounting",
        "construction",
        "reports",
    ],
    
    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "inventory": [{
            "name": "Inventory Reports",
            "url": "/admin/reports/",
            "icon": "fas fa-chart-line",
            "permissions": ["inventory.view_product"]
        }],
        "construction": [{
            "name": "Site Reports",
            "url": "/admin/construction/site/",
            "icon": "fas fa-building",
            "permissions": ["construction.view_site"]
        }],
    },
    
    # Custom icons for side menu apps/models
    "icons": {
        # Organization
        "tenants.Tenant": "fas fa-building",
        "auth.User": "fas fa-users",
        "auth.Group": "fas fa-users-cog",
        "users.User": "fas fa-user-tie",
        
        # Inventory
        "inventory.Product": "fas fa-box",
        "inventory.Category": "fas fa-tags",
        "inventory.Warehouse": "fas fa-warehouse",
        "inventory.Stock": "fas fa-boxes",
        "inventory.StockMovement": "fas fa-exchange-alt",
        "inventory.UnitOfMeasure": "fas fa-ruler",
        
        # Sales
        "sales.Customer": "fas fa-user-friends",
        "sales.SalesOrder": "fas fa-shopping-cart",
        "sales.Quotation": "fas fa-file-invoice",
        "sales.Invoice": "fas fa-file-invoice-dollar",
        "sales.CreditNote": "fas fa-receipt",
        "sales.PaymentReceived": "fas fa-money-bill-wave",
        "sales.CustomerLedger": "fas fa-book",
        
        # Purchase
        "purchase.Supplier": "fas fa-truck",
        "purchase.PurchaseRequest": "fas fa-clipboard-list",
        "purchase.PurchaseOrder": "fas fa-shopping-bag",
        "purchase.PurchaseInvoice": "fas fa-file-invoice",
        "purchase.DebitNote": "fas fa-receipt",
        
        # Accounting
        "accounting.Account": "fas fa-chart-pie",
        "accounting.JournalEntry": "fas fa-book-open",
        "accounting.BankAccount": "fas fa-university",
        "accounting.BankTransaction": "fas fa-exchange-alt",
        "accounting.TaxRule": "fas fa-percent",
        "accounting.VATReturn": "fas fa-file-alt",
        
        # Construction
        "construction.Site": "fas fa-hard-hat",
        "construction.Worker": "fas fa-user-hard-hat",
        "construction.Attendance": "fas fa-calendar-check",
        "construction.DailyLog": "fas fa-clipboard",
        "construction.MaterialConsumption": "fas fa-tools",
        "construction.Equipment": "fas fa-tractor",
        "construction.EquipmentUsageLog": "fas fa-clipboard-list",
    },
    
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    #################
    # Related Modal #
    #################
    
    # Use modals instead of popups
    "related_modal_active": False,
    
    #############
    # UI Tweaks #
    #############
    
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": "admin/css/admin_custom.css",
    "custom_js": "admin/js/fontawesome_loader.js",
    
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    
    ###############
    # Change view #
    ###############
    
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    
    # Override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "horizontal_tabs",
        "inventory.product": "horizontal_tabs",
        "sales.invoice": "horizontal_tabs",
        "purchase.purchaseorder": "horizontal_tabs",
    },
    
    # Add a language dropdown into the admin
    "language_chooser": False,
}

# ============================================================================
# JAZZMIN UI TWEAKS - Custom Theme Configuration
# ============================================================================

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-indigo",
    "accent": "accent-indigo",
    "navbar": "navbar-white navbar-light",  # Light navbar for better contrast
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",  # Clean, professional theme
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": True
}
