# Backend Scripts

This folder contains utility scripts for the Khata ERP backend.

## Available Scripts

### Data Management Scripts

#### `check_tenant_data.py`
Check tenant data integrity and display statistics.

**Usage:**
```bash
cd backend
python scripts/check_tenant_data.py
```

#### `create_tenant_data.py`
Create sample tenant data for testing and development.

**Usage:**
```bash
python scripts/create_tenant_data.py
```

#### `seed_all_tenants.py`
Seed all tenants with demo data.

**Usage:**
```bash
python scripts/seed_all_tenants.py
```

#### `seed_basic_inventory_data.py`
Seed basic inventory data (categories, units, products).

**Usage:**
```bash
python scripts/seed_basic_inventory_data.py
```

### Code Maintenance Scripts

#### `fix_all_viewsets.py`
Fix and update all ViewSets to follow best practices.

**Usage:**
```bash
python scripts/fix_all_viewsets.py
```

#### `fix_formatting.py`
Fix code formatting issues across the codebase.

**Usage:**
```bash
python scripts/fix_formatting.py
```

## Notes

- All scripts should be run from the `backend` directory
- Scripts may require Django environment to be loaded
- Some scripts may modify the database - use with caution in production
- Always backup your database before running data modification scripts

## Adding New Scripts

When adding new scripts:
1. Place them in this `scripts/` folder
2. Add documentation to this README
3. Include usage examples
4. Add error handling and logging
5. Test thoroughly before committing

## Best Practices

- Use `python manage.py shell` for interactive Django operations
- Use management commands (`manage.py` commands) for production scripts
- Keep scripts idempotent when possible
- Add progress indicators for long-running scripts
- Log all important operations
