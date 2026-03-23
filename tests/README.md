# Backend Tests

This folder contains all test files for the Khata ERP backend.

## Test Files

### API Tests
- `test_api.py` - General API tests
- `test_api_tenant_context.py` - Tenant context API tests
- `test_dashboard_api.py` - Dashboard API tests
- `test_product_api.py` - Product API tests
- `test_register_api.py` - Registration API tests

### Authentication Tests
- `test_jwt_login.py` - JWT authentication tests
- `test_register.py` - User registration tests
- `test_registration_complete.py` - Complete registration flow tests

### Tenant Tests
- `test_tenant_creation.py` - Tenant creation tests
- `test_tenant_filtering.py` - Tenant filtering tests
- `test_tenant_refresh_flow.py` - Tenant refresh flow tests
- `test_tenant_user_flow.py` - Tenant user flow tests

### Product Tests
- `test_product_create.py` - Product creation tests
- `test_product_create_debug.py` - Product creation debugging tests
- `test_product_creation.py` - Product creation flow tests
- `test_create_product.py` - Create product tests

### Module Tests
- `test_construction_workflow.py` - Construction module workflow tests
- `test_category_tenant_issue.py` - Category tenant issue tests
- `test_slug_generation.py` - Slug generation tests

### Verification Scripts
- `verify_credit_system.py` - Credit system verification script

## Running Tests

### Run all tests
```bash
cd backend
python manage.py test tests
```

### Run specific test file
```bash
python manage.py test tests.test_api
```

### Run with pytest (if installed)
```bash
pytest tests/
```

### Run specific test
```bash
pytest tests/test_api.py::TestClassName::test_method_name
```

## Test Structure

All tests should follow Django's testing conventions:
- Use `django.test.TestCase` for database tests
- Use `rest_framework.test.APITestCase` for API tests
- Use `django.test.TransactionTestCase` for transaction tests
- Use fixtures for test data
- Clean up after tests

## Coverage

To run tests with coverage:
```bash
coverage run --source='.' manage.py test tests
coverage report
coverage html
```

## Notes

- All tests use the test database (automatically created and destroyed)
- Tests are isolated and should not depend on each other
- Use factories or fixtures for test data
- Mock external services when necessary
