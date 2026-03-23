from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, AuditLog
from tenants.models import Tenant


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that includes user role and tenant information in the response.
    """
    
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
        data = super().validate(attrs)
        
        # Add user information to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'permissions': {
                'is_admin': self.user.is_admin,
                'is_manager': self.user.is_manager,
                'is_supervisor': self.user.is_supervisor,
                'is_accountant': self.user.is_accountant,
                'is_viewer': self.user.is_viewer,
                'can_approve_purchases': self.user.can_approve_purchases(),
                'can_manage_users': self.user.can_manage_users(),
                'can_view_financials': self.user.can_view_financials(),
                'can_edit_data': self.user.can_edit_data(),
                'modules': {
                    'sales': self.user.has_module_access('sales'),
                    'purchase': self.user.has_module_access('purchase'),
                    'inventory': self.user.has_module_access('inventory'),
                    'construction': self.user.has_module_access('construction'),
                    'accounting': self.user.has_module_access('accounting'),
                    'reports': self.user.has_module_access('reports'),
                    'pos': self.user.has_module_access('pos'),
                    'hr': self.user.has_module_access('hr'),
                }
            }
        }
        
        # Add tenant information to the response
        if self.user.tenant:
            data['tenant'] = {
                'id': self.user.tenant.id,
                'name': self.user.tenant.name,
                'slug': self.user.tenant.slug,
                'business_type': self.user.tenant.business_type,
                'plan_type': self.user.tenant.plan_type,
                'active_modules': self.user.tenant.active_modules,
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
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'tenant', 'password', 'is_active', 'last_login', 'date_joined', 'permissions']
        read_only_fields = ['id', 'tenant', 'last_login', 'date_joined', 'permissions']
    
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
        """Update user, handle password separately"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    tenant_name = serializers.CharField(write_only=True, required=True, help_text="Organization name for new tenant creation")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'tenant_name']
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered. Please use a different email or login.')
        return value
    
    def validate_tenant_name(self, value):
        """Ensure tenant name is unique"""
        if value and Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError('An organization with this name already exists. Please choose a different name.')
        return value
    
    def create(self, validated_data):
        try:
            # Extract tenant_name
            tenant_name = validated_data.pop('tenant_name')
            
            # Create tenant first (mark as created from registration)
            tenant = Tenant.objects.create(
                name=tenant_name,
                business_type='other',
                plan_type='free',
                active_modules=['sales', 'purchase', 'inventory', 'accounting', 'construction', 'reports'],
                created_from_registration=True  # Mark as registration tenant
            )
            
            # Create user as admin of the new tenant
            user = User.objects.create_user(
                **validated_data,
                tenant=tenant,
                role='admin'  # First user is always admin
            )
            
            # Set created_by on tenant
            tenant.created_by = user
            tenant.save()
            
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
