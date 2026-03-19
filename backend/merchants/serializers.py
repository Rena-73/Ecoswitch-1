from rest_framework import serializers
from .models import Store, MerchantProfile, MerchantProduct, MerchantOrder, OrderItem, MerchantAnalytics


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer for store information
    """
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ('merchant', 'created_at', 'updated_at')


class MerchantRegistrationSerializer(serializers.Serializer):
    """
    Serializer for merchant registration with store information
    """
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    
    # Merchant profile fields
    business_name = serializers.CharField(max_length=200)
    business_type = serializers.CharField(max_length=100)
    business_description = serializers.CharField()
    contact_person = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    
    # Store fields
    store_name = serializers.CharField(max_length=200)
    street_address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100, default='India')
    postal_code = serializers.CharField(max_length=20)
    
    def validate_postal_code(self, value):
        """Validate postal code format"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Postal code must be 6 digits")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        import re
        # More flexible phone number validation for international numbers
        if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', value):
            raise serializers.ValidationError("Please enter a valid phone number (10-15 digits)")
        return value


class MerchantProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for merchant profiles
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = MerchantProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class MerchantProductSerializer(serializers.ModelSerializer):
    """
    Serializer for merchant products
    """
    merchant_business_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = MerchantProduct
        fields = '__all__'
        read_only_fields = ('merchant', 'created_at', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'


class MerchantOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for merchant orders
    """
    items = OrderItemSerializer(many=True, read_only=True)
    merchant_business_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = MerchantOrder
        fields = '__all__'
        read_only_fields = ('merchant', 'created_at', 'updated_at')


class MerchantAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for merchant analytics
    """
    merchant_business_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = MerchantAnalytics
        fields = '__all__'
        read_only_fields = ('merchant', 'created_at')

















