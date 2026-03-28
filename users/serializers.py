from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, AuditLog
from tenants.models import Tenant


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that includes user role and tenant information in the response.
    Accepts email instead of username for login.
    """
    
    # Override username_field to use email
    username_field = 'email'
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token
        token['role'] = user.role
        token['tenant_id'] = user.tenant.id if user.tenant else None
        token['tenant_slug'] = user.tenant.slug if user.tenant else None
        token['tenant_name'] = user.tenant.name if user.tenant else None
        
        return token
    
    def validate(self, attrs):
        # Use email for authentication
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authenticate using email
            from django.contrib.auth import authenticate
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    {'detail': 'No active account found with the given credentials'},
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                {'detail': 'Must include "email" and "password".'},
                code='authorization'
            )
        
        # Generate tokens
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Add user information to the response
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'permissions': {
                'is_admin': user.is_admin,
                'is_manager': user.is_manager,
                'is_supervisor': user.is_supervisor,
                'is_accountant': user.is_accountant,
                'is_viewer': user.is_viewer,
                'can_approve_purchases': user.can_approve_purchases(),
                'can_manage_users': user.can_manage_users(),
                'can_view_financials': user.can_view_financials(),
                'can_edit_data': user.can_edit_data(),
                'modules': {
                    'sales': user.has_module_access('sales'),
                    'purchase': user.has_module_access('purchase'),
                    'inventory': user.has_module_access('inventory'),
                    'construction': user.has_module_access('construction'),
                    'accounting': user.has_module_access('accounting'),
                    'reports': user.has_module_access('reports'),
                    'pos': user.has_module_access('pos'),
                    'hr': user.has_module_access('hr'),
                }
            }
        }
        
        # Add tenant information to the response
        if user.tenant:
            data['tenant'] = {
                'id': user.tenant.id,
                'name': user.tenant.name,
                'slug': user.tenant.slug,
                'business_type': user.tenant.business_type,
                'plan_type': user.tenant.plan_type,
                'active_modules': user.tenant.active_modules,
            }
        else:
            data['tenant'] = None
        
        return data


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'business_type', 'is_active', 'plan_type', 'active_modules']
        read_only_fields = ['id', 'slug']


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    permissions = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'tenant', 'password', 'is_active', 'last_login', 'date_joined', 'permissions']
        read_only_fields = ['id', 'tenant', 'last_login', 'date_joined', 'permissions']
    
    def get_role(self, obj):
        """
        Get the tenant-specific role from UserTenantMembership if available,
        otherwise fall back to the user's global role.
        """
        # Get the current request's tenant from context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.tenant:
            # Import here to avoid circular import
            from tenants.membership_models import UserTenantMembership
            
            # Get the membership for this user in the current tenant
            membership = UserTenantMembership.objects.filter(
                user=obj,
                tenant=request.user.tenant
            ).first()
            
            if membership:
                return membership.role
        
        # Fall back to user's global role
        return obj.role
    
    def get_permissions(self, obj):
        """Get user permissions including module access"""
        return {
            'is_admin': obj.is_admin,
            'is_manager': obj.is_manager,
            'is_supervisor': obj.is_supervisor,
            'is_accountant': obj.is_accountant,
            'is_viewer': obj.is_viewer,
            'can_approve_purchases': obj.can_approve_purchases(),
            'can_manage_users': obj.can_manage_users(),
            'can_view_financials': obj.can_view_financials(),
            'can_edit_data': obj.can_edit_data(),
            'modules': {
                'sales': obj.has_module_access('sales'),
                'purchase': obj.has_module_access('purchase'),
                'inventory': obj.has_module_access('inventory'),
                'construction': obj.has_module_access('construction'),
                'accounting': obj.has_module_access('accounting'),
                'reports': obj.has_module_access('reports'),
                'pos': obj.has_module_access('pos'),
                'hr': obj.has_module_access('hr'),
            }
        }
    
    def create(self, validated_data):
        """Create user with password"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_password('changeme123')  # Default password
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, handle password and role separately"""
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle password update
        if password:
            instance.set_password(password)
        
        # Handle role update - update both global role and membership role
        if role:
            instance.role = role
            
            # Also update the membership role for the current tenant
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.tenant:
                from tenants.membership_models import UserTenantMembership
                
                membership = UserTenantMembership.objects.filter(
                    user=instance,
                    tenant=request.user.tenant
                ).first()
                
                if membership:
                    membership.role = role
                    membership.save()
        
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    tenant_name = serializers.CharField(write_only=True, required=False, help_text="Organization name for new tenant creation (auto-generated if not provided)")
    username = serializers.CharField(required=False, help_text="Username (auto-generated from email if not provided)")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'tenant_name']
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered. Please use a different email or login.')
        return value
    
    def validate_tenant_name(self, value):
        """Ensure tenant name is unique (if provided)"""
        if value and Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError('An organization with this name already exists. Please choose a different name.')
        return value
    
    def create(self, validated_data):
        try:
            # Auto-generate tenant_name if not provided
            tenant_name = validated_data.pop('tenant_name', None)
            if not tenant_name:
                first_name = validated_data.get('first_name', '')
                last_name = validated_data.get('last_name', '')
                tenant_name = f"{first_name} {last_name}'s Organization".strip()
                
                # Ensure uniqueness by appending number if needed
                base_name = tenant_name
                counter = 1
                while Tenant.objects.filter(name=tenant_name).exists():
                    tenant_name = f"{base_name} {counter}"
                    counter += 1
            
            # Auto-generate username from email if not provided
            if 'username' not in validated_data or not validated_data['username']:
                email = validated_data.get('email', '')
                username = email.split('@')[0] if email else 'user'
                
                # Ensure uniqueness by appending number if needed
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                validated_data['username'] = username
            
            # Create tenant first (mark as created from registration)
            tenant = Tenant.objects.create(
                name=tenant_name,
                business_type='other',
                plan_type='free',
                active_modules=['sales', 'purchase', 'inventory', 'accounting', 'construction', 'reports'],
                created_from_registration=True  # Mark as registration tenant
            )
            
            # Initialize default permissions for the new tenant
            from .permission_models import initialize_tenant_permissions
            initialize_tenant_permissions(tenant)
            
            # Create user as admin of the new tenant
            user = User.objects.create_user(
                **validated_data,
                tenant=tenant,
                role='admin'  # First user is always admin
            )
            
            # Set created_by on tenant
            tenant.created_by = user
            tenant.save()
            
            # Create membership record for the owner
            from tenants.membership_models import UserTenantMembership
            UserTenantMembership.objects.create(
                user=user,
                tenant=tenant,
                role='admin'
            )
            
            return user
        except serializers.ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Handle specific database errors
            error_msg = str(e)
            if 'UNIQUE constraint failed: users.username' in error_msg:
                raise serializers.ValidationError({
                    'username': 'This username is already taken. Please choose a different username.'
                })
            elif 'UNIQUE constraint failed: users.email' in error_msg:
                raise serializers.ValidationError({
                    'email': 'This email is already registered. Please use a different email or login.'
                })
            else:
                raise serializers.ValidationError({
                    'detail': f'Registration failed: {error_msg}'
                })



class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display', 'module',
            'description', 'ip_address', 'metadata', 'created_at'
        ]
        read_only_fields = fields
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "System"



class RolePermissionSerializer(serializers.Serializer):
    """
    Serializer for role permissions.
    Returns permissions in a format suitable for the frontend permissions matrix.
    """
    role = serializers.CharField()
    permissions = serializers.DictField(child=serializers.BooleanField())


class PermissionsMatrixSerializer(serializers.Serializer):
    """
    Serializer for the complete permissions matrix.
    Returns all roles with their permissions.
    """
    Admin = serializers.DictField(child=serializers.BooleanField())
    Manager = serializers.DictField(child=serializers.BooleanField())
    Supervisor = serializers.DictField(child=serializers.BooleanField())
    Accountant = serializers.DictField(child=serializers.BooleanField())
    Viewer = serializers.DictField(child=serializers.BooleanField())


class UpdatePermissionsSerializer(serializers.Serializer):
    """
    Serializer for updating permissions.
    Accepts the complete permissions matrix from the frontend.
    """
    Admin = serializers.DictField(child=serializers.BooleanField(), required=False)
    Manager = serializers.DictField(child=serializers.BooleanField(), required=False)
    Supervisor = serializers.DictField(child=serializers.BooleanField(), required=False)
    Accountant = serializers.DictField(child=serializers.BooleanField(), required=False)
    Viewer = serializers.DictField(child=serializers.BooleanField(), required=False)
