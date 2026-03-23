# Khata Backend - Multi-Tenant ERP System

A comprehensive Django-based multi-tenant ERP system designed for hardware stores, construction businesses, and general retail operations in Nepal. Built with Django REST Framework and featuring complete tenant isolation, role-based access control, and modular business applications.

## Features

### Core Capabilities
- **Multi-Tenancy**: Shared database architecture with complete tenant isolation
- **Authentication & Authorization**: JWT-based auth with role-based access control (RBAC)
- **RESTful API**: Comprehensive REST API with OpenAPI/Swagger documentation
- **Admin Interface**: Enhanced Django admin with Jazzmin UI

### Business Modules
- **Inventory Management**: Products, categories, stock tracking, and warehouse management
- **Sales Management**: Quotations, orders, invoices, credit notes, and customer management
- **Purchase Management**: Purchase orders, supplier management, and procurement tracking
- **Accounting**: General ledger, journal entries, and financial reporting
- **Construction Module**: Site management, material consumption, and labor tracking
- **Reports & Analytics**: Comprehensive reporting engine with dashboard metrics

### Advanced Features
- **Udhaar (Credit) System**: Customer credit management with payment tracking
- **Multi-Site Support**: Manage multiple locations per tenant
- **Demo Data Seeding**: Quick setup with sample data for testing
- **Tenant Filtering**: Automatic data isolation at the query level

## Tech Stack

- **Framework**: Django 5.0
- **API**: Django REST Framework 3.14+
- **Authentication**: djangorestframework-simplejwt 5.3+
- **Database**: PostgreSQL (via psycopg2-binary)
- **Admin UI**: django-jazzmin 3.0+
- **API Documentation**: drf-spectacular 0.27+
- **CORS**: django-cors-headers 4.3+
- **Filtering**: django-filter 23.5+
- **Configuration**: python-decouple 3.8+
- **Image Processing**: Pillow 10.2+

## Project Structure

```
backend/
├── core_backend/              # Main Django project
│   ├── settings.py           # Project configuration
│   ├── urls.py               # Root URL routing
│   ├── management/           # Custom management commands
│   │   └── commands/
│   │       └── seed_demo_data.py  # Demo data seeding
│   └── django_py314_patch.py # Python 3.14 compatibility
│
├── tenants/                  # Multi-tenancy management
│   ├── models.py            # Tenant model
│   ├── middleware.py        # Tenant isolation middleware
│   ├── views.py             # Tenant CRUD operations
│   └── serializers.py       # Tenant serializers
│
├── users/                    # User management & auth
│   ├── models.py            # Custom User model with RBAC
│   ├── views.py             # Auth endpoints
│   ├── serializers.py       # User serializers
│   └── permissions.py       # Custom permissions
│
├── inventory/                # Inventory management
│   ├── models.py            # Product, Category, Stock models
│   ├── views.py             # Inventory API endpoints
│   ├── serializers.py       # Inventory serializers
│   ├── services.py          # Business logic layer
│   └── permissions.py       # Inventory permissions
│
├── sales/                    # Sales management
│   ├── models.py            # Customer, Order, Invoice models
│   ├── views.py             # Sales API endpoints
│   ├── serializers.py       # Sales serializers
│   └── admin.py             # Sales admin configuration
│
├── purchase/                 # Purchase management
│   ├── models.py            # Supplier, PurchaseOrder models
│   ├── views.py             # Purchase API endpoints
│   └── serializers.py       # Purchase serializers
│
├── accounting/               # Accounting module
│   ├── models.py            # Account, JournalEntry models
│   ├── views.py             # Accounting API endpoints
│   ├── serializers.py       # Accounting serializers
│   └── services.py          # Accounting business logic
│
├── construction/             # Construction management
│   ├── models.py            # Site, MaterialConsumption models
│   ├── views.py             # Construction API endpoints
│   └── serializers.py       # Construction serializers
│
├── reports/                  # Reports & analytics
│   ├── views.py             # Report generation endpoints
│   └── admin.py             # Report admin interface
│
├── utils/                    # Shared utilities
│   └── models.py            # TenantModel base class
│
├── static/                   # Static files
│   └── admin/               # Admin customizations
│
└── scripts/                  # Utility scripts
    ├── seed_basic_inventory_data.py
    └── create_tenant_data.py
```

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip or virtualenv

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ramoniswack/khata-backend.git
cd khata-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

Required environment variables:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_NAME=khata_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

5. **Setup database**
```bash
# Create PostgreSQL database
createdb khata_db

# Run migrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Seed demo data (optional)**
```bash
python manage.py seed_demo_data
```

8. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Documentation

### Access Swagger UI
Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Admin Interface
Access the enhanced admin interface at:
- **Admin Panel**: `http://localhost:8000/admin/`

### Key API Endpoints

#### Authentication
```
POST   /api/auth/register/          # User registration
POST   /api/auth/login/             # Login (get JWT tokens)
POST   /api/auth/token/refresh/     # Refresh access token
GET    /api/auth/profile/           # Get user profile
PUT    /api/auth/profile/           # Update user profile
```

#### Tenants
```
GET    /api/tenants/                # List tenants
POST   /api/tenants/                # Create tenant
GET    /api/tenants/{id}/           # Get tenant details
PUT    /api/tenants/{id}/           # Update tenant
DELETE /api/tenants/{id}/           # Delete tenant
```

#### Inventory
```
GET    /api/inventory/products/     # List products
POST   /api/inventory/products/     # Create product
GET    /api/inventory/categories/   # List categories
POST   /api/inventory/stock-in/     # Record stock in
POST   /api/inventory/stock-out/    # Record stock out
```

#### Sales
```
GET    /api/sales/customers/        # List customers
POST   /api/sales/quotations/       # Create quotation
POST   /api/sales/orders/           # Create sales order
POST   /api/sales/invoices/         # Create invoice
GET    /api/sales/credit-notes/     # List credit notes
```

#### Purchase
```
GET    /api/purchase/suppliers/     # List suppliers
POST   /api/purchase/orders/        # Create purchase order
GET    /api/purchase/orders/{id}/   # Get purchase order
```

#### Reports
```
GET    /api/reports/dashboard/      # Dashboard metrics
GET    /api/reports/sales/          # Sales reports
GET    /api/reports/inventory/      # Inventory reports
GET    /api/reports/financial/      # Financial reports
```

## Multi-Tenancy Architecture

### How It Works

1. **Tenant Model**: Each tenant has a unique slug and configuration
2. **User Association**: Users belong to one or more tenants
3. **Middleware**: `TenantMiddleware` extracts tenant from authenticated user
4. **Thread-Local Storage**: Current tenant stored in thread-local variable
5. **Automatic Filtering**: `TenantManager` filters all queries by current tenant
6. **Base Model**: `TenantModel` provides automatic tenant assignment

### Data Isolation

All tenant-scoped models inherit from `TenantModel`:

```python
from utils.models import TenantModel

class Product(TenantModel):
    name = models.CharField(max_length=255)
    # tenant field automatically added
    # queries automatically filtered
```

This ensures:
- Complete data isolation between tenants
- No cross-tenant data leakage
- Automatic tenant assignment on creation
- Simplified query logic

## Role-Based Access Control

### User Roles
- **Admin**: Full system access
- **Manager**: Business operations management
- **Supervisor**: Operational oversight
- **Accountant**: Financial operations
- **Staff**: Basic operations

### Permission System
Custom permissions defined per module:
- View, create, update, delete permissions
- Site-specific access control
- Module-level restrictions

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines. Use:
```bash
flake8 .
black .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Custom Management Commands
```bash
# Seed demo data
python manage.py seed_demo_data

# Other scripts in scripts/ directory
python scripts/create_tenant_data.py
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up static files serving
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up backup strategy

### Environment Variables
```env
DEBUG=False
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: [your-email@example.com]

## Acknowledgments

Built with Django and Django REST Framework. Special thanks to the open-source community.
