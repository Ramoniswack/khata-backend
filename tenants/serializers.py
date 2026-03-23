from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model"""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'business_type', 'owner_name', 'email',
            'phone', 'address', 'is_active', 'plan_type', 'active_modules',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'created_by']


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new tenant"""
    
    # Include read-only fields in response
    id = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'slug', 'name', 'business_type', 'owner_name', 'email',
            'phone', 'address', 'active_modules'
        ]
        read_only_fields = ['id', 'slug']
    
    def validate_name(self, value):
        """Ensure tenant name is unique"""
        if Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError('An organization with this name already exists.')
        return value
    
    def create(self, validated_data):
        """Create tenant with default values"""
        # Set default modules if not provided
        if 'active_modules' not in validated_data or not validated_data['active_modules']:
            validated_data['active_modules'] = [
                'inventory', 'sales', 'purchase', 'accounting', 'reports'
            ]
        
        # Set default plan
        validated_data['plan_type'] = 'free'
        validated_data['is_active'] = True
        
        return super().create(validated_data)


class TenantProfileSerializer(serializers.ModelSerializer):
    """Serializer for public tenant profile (accessed by slug)"""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'business_type', 'is_active',
            'plan_type', 'active_modules'
        ]
        read_only_fields = fields
