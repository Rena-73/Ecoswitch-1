from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant, 
    ProductReview, Coupon, Payment, ShippingMethod, OrderTracking, EcoImpact
)
from customers.models import Cart, CartItem, CustomerProfile, CustomerOrder, OrderItem, CustomerWishlist

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for product brands"""
    class Meta:
        model = Brand
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'sort_order']
    
    def get_image_url(self, obj):
        """Get full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants"""
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'stock_quantity', 'is_active']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user_name', 'user_email', 'rating', 'title', 'comment', 
                 'is_verified_purchase', 'created_at']
        read_only_fields = ['user', 'is_verified_purchase']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view with essential fields"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category_name', 'brand_name',
            'price', 'compare_price', 'primary_image', 'discount_percentage',
            'stock_quantity', 'is_in_stock', 'is_low_stock', 'eco_rating',
            'is_organic', 'is_biodegradable', 'is_recyclable', 'is_plastic_free',
            'carbon_footprint', 'is_featured', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image URL"""
        try:
            primary_image = obj.images.filter(is_primary=True).first()
            if primary_image and primary_image.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(primary_image.image.url)
                return primary_image.image.url
            return None
        except Exception:
            return None
    
    def get_average_rating(self, obj):
        """Calculate average rating from reviews"""
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(avg_rating=serializers.Avg('rating'))['avg_rating'], 1)
        return 0.0
    
    def get_review_count(self, obj):
        """Get total review count"""
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(ProductListSerializer):
    """Serializer for product detail view with all fields"""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    description = serializers.CharField()
    
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'sku', 'images', 'variants', 'reviews',
            'meta_title', 'meta_description'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product_name = serializers.CharField(read_only=True)
    product_image = serializers.CharField(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'product_image', 
                 'product_price', 'quantity', 'total_price', 'created_at']
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        """Validate product ID and availability"""
        try:
            # Try to convert to int first, then search
            product_id = int(value)
            product = Product.objects.get(id=product_id, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
            return str(product_id)  # Return as string for consistency
        except (ValueError, Product.DoesNotExist):
            raise serializers.ValidationError("Product not found or inactive")


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_image', 
                 'quantity', 'unit_price', 'total_price']


class CustomerOrderSerializer(serializers.ModelSerializer):
    """Serializer for customer orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.first_name', read_only=True)
    customer_email = serializers.CharField(source='customer.user.email', read_only=True)
    
    class Meta:
        model = CustomerOrder
        fields = [
            'id', 'order_number', 'customer_name', 'customer_email',
            'total_amount', 'shipping_cost', 'tax_amount', 'discount_amount',
            'shipping_address', 'order_status', 'payment_status', 'payment_method',
            'items', 'created_at', 'updated_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders"""
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['upi', 'credit_card', 'debit_card', 'net_banking', 'cod'],
        default='upi'
    )
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons"""
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'coupon_type', 'value', 
                 'minimum_amount', 'maximum_discount', 'usage_limit', 'used_count',
                 'valid_from', 'valid_until', 'is_active', 'is_valid']


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying coupons"""
    coupon_code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'order', 'order_number', 'amount', 
                 'payment_method', 'payment_status', 'gateway_transaction_id',
                 'gateway_response', 'created_at', 'updated_at', 'paid_at']


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods"""
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'cost', 'free_shipping_threshold', 
                 'estimated_days', 'is_active']


class OrderTrackingSerializer(serializers.ModelSerializer):
    """Serializer for order tracking"""
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'description', 'location', 'timestamp']


class EcoImpactSerializer(serializers.ModelSerializer):
    """Serializer for eco impact tracking"""
    class Meta:
        model = EcoImpact
        fields = ['id', 'co2_saved', 'plastic_avoided', 'water_saved', 
                 'trees_planted', 'created_at']


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    class Meta:
        model = CustomerWishlist
        fields = ['id', 'product_id', 'product_name', 'product_image', 
                 'product_price', 'created_at']


class AddToWishlistSerializer(serializers.Serializer):
    """Serializer for adding items to wishlist"""
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    product_image = serializers.URLField(required=False, allow_blank=True)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_product_id(self, value):
        """Validate product ID"""
        try:
            product_id = int(value)
            product = Product.objects.get(id=product_id, is_active=True)
            return str(product_id)
        except (ValueError, Product.DoesNotExist):
            raise serializers.ValidationError("Product not found or inactive")