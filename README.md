# Khata - Multi-Tenant SaaS ERP for Nepal

A Django-based multi-tenant ERP system with shared database architecture.

## Tech Stack

- Django 5.x
- Django REST Framework
- PostgreSQL
- SimpleJWT for authentication
- Multi-tenancy: Shared database with tenant ForeignKey

## Project Structure

```
core_backend/          # Main Django project
├── settings.py        # Project settings with JWT & DRF config
├── urls.py           # Root URL configuration
├── wsgi.py           # WSGI application
└── asgi.py           # ASGI application

tenants/              # Tenant management app
├── models.py         # Tenant model (name, slug, plan_type)
└── middleware.py     # TenantMiddleware for global tenant filtering

users/                # User management & authentication
├── models.py         # Custom User model with tenant FK and RBAC
├── serializers.py    # User serializers
├── views.py          # Auth views (register, profile)
└── urls.py           # Auth endpoints

inventory/            # Inventory management
├── models.py         # Product & Stock models (tenant-scoped)
└── admin.py          # Admin configuration

utils/                # Shared utilities
└── models.py         # TenantModel abstract base class
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL database in `core_backend/settings.py`

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## Key Features

### Multi-Tenancy Architecture
- Shared database with tenant ForeignKey on all models
- Thread-local tenant storage via middleware
- Automatic tenant filtering on all queries
- TenantModel base class for easy tenant-scoped models

### Authentication & Authorization
- JWT-based authentication (SimpleJWT)
- Role-based access control (Admin, Manager, Supervisor, Accountant)
- Custom User model with tenant association

### API Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET/PUT /api/auth/profile/` - User profile

## How Tenant Isolation Works

1. User authenticates and receives JWT token
2. TenantMiddleware extracts tenant from authenticated user
3. Tenant stored in thread-local storage
4. TenantManager automatically filters all queries by current tenant
5. TenantModel auto-assigns tenant on save

This ensures complete data isolation between tenants at the database query level.
