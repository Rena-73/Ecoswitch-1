from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
import logging

from .models import (
    Category, Brand, Product, ProductImage, ProductVariant, 
    ProductReview, Coupon, Payment, ShippingMethod, OrderTracking, EcoImpact
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer, ProductDetailSerializer,
    ProductReviewSerializer, CartSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    CustomerOrderSerializer, CreateOrderSerializer, CouponSerializer, ApplyCouponSerializer,
    PaymentSerializer, ShippingMethodSerializer, OrderTrackingSerializer, EcoImpactSerializer,
    WishlistItemSerializer, AddToWishlistSerializer
)
from customers.models import Cart, CartItem, CustomerProfile, CustomerOrder, OrderItem, CustomerWishlist

User = get_user_model()
logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for product categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for product brands"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products with filtering and search capabilities"""
    queryset = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images', 'reviews')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by brand
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by eco attributes
        eco_rating = self.request.query_params.get('eco_rating')
        if eco_rating:
            queryset = queryset.filter(eco_rating__gte=eco_rating)
        
        is_organic = self.request.query_params.get('is_organic')
        if is_organic == 'true':
            queryset = queryset.filter(is_organic=True)
        
        is_plastic_free = self.request.query_params.get('is_plastic_free')
        if is_plastic_free == 'true':
            queryset = queryset.filter(is_plastic_free=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Sort
        sort = self.request.query_params.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'eco_rating':
            queryset = queryset.order_by('-eco_rating')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-reviews__rating')
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, pk=None):
        """Add a product review"""
        product = self.get_object()
        serializer = ProductReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if user already reviewed this product
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                return Response(
                    {'error': 'You have already reviewed this product'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for shopping cart management with comprehensive functionality"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        cart, created = Cart.objects.get_or_create(customer=customer_profile)
        return Cart.objects.filter(customer=customer_profile)
    
    def list(self, request, *args, **kwargs):
        """Get current user's cart with all items"""
        try:
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart, created = Cart.objects.get_or_create(customer=customer_profile)
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching cart: {str(e)}")
            return Response(
                {'error': 'Failed to fetch cart'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_item(self, request):
        """Add item to cart with proper validation and error handling"""
        try:
            serializer = AddToCartSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart, created = Cart.objects.get_or_create(customer=customer_profile)
            
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            # Get product with proper error handling
            try:
                product_id_int = int(product_id)
                product = Product.objects.get(id=product_id_int, is_active=True)
            except (ValueError, Product.DoesNotExist):
                return Response(
                    {'error': 'Product not found or inactive'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check stock availability
            if product.track_inventory and product.stock_quantity < quantity:
                return Response(
                    {'error': f'Only {product.stock_quantity} items available in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={
                    'product_name': product.name,
                    'product_image': self._get_product_image_url(product),
                    'product_price': product.price,
                    'quantity': quantity
                }
            )
            
            if not created:
                # Update quantity if item already exists
                cart_item.quantity += quantity
                cart_item.save()
            
            # Return updated cart data
            cart.refresh_from_db()
            serializer = self.get_serializer(cart)
            return Response({
                'message': 'Item added to cart successfully',
                'cart': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response(
                {'error': 'Failed to add item to cart'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_item(self, request):
        """Update cart item quantity"""
        try:
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart = get_object_or_404(Cart, customer=customer_profile)
            
            item_id = request.data.get('item_id')
            quantity = request.data.get('quantity')
            
            if not item_id or quantity is None:
                return Response(
                    {'error': 'item_id and quantity are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Cart item not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if quantity <= 0:
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            
            cart_item.quantity = quantity
            cart_item.save()
            
            # Return updated cart data
            cart.refresh_from_db()
            serializer = self.get_serializer(cart)
            return Response({
                'message': 'Cart item updated successfully',
                'cart': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response(
                {'error': 'Failed to update cart item'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def remove_item(self, request):
        """Remove item from cart"""
        try:
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart = get_object_or_404(Cart, customer=customer_profile)
            
            item_id = request.data.get('item_id')
            
            if not item_id:
                return Response(
                    {'error': 'item_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.delete()
                
                # Return updated cart data
                cart.refresh_from_db()
                serializer = self.get_serializer(cart)
                return Response({
                    'message': 'Item removed from cart successfully',
                    'cart': serializer.data
                })
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Cart item not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}")
            return Response(
                {'error': 'Failed to remove cart item'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def clear(self, request):
        """Clear all items from cart"""
        try:
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart = get_object_or_404(Cart, customer=customer_profile)
            
            cart.items.all().delete()
            return Response({'message': 'Cart cleared successfully'})
            
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            return Response(
                {'error': 'Failed to clear cart'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_product_image_url(self, product):
        """Helper method to get product image URL"""
        try:
            primary_image = product.images.filter(is_primary=True).first()
            if primary_image and primary_image.image:
                return primary_image.image.url
            return ''
        except Exception:
            return ''


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for order management with comprehensive functionality"""
    serializer_class = CustomerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        return CustomerOrder.objects.filter(customer=customer_profile)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_order(self, request):
        """Create a new order from cart with proper validation"""
        try:
            serializer = CreateOrderSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            cart, created = Cart.objects.get_or_create(customer=customer_profile)
            
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Create order
                order_number = f"ECO{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
                order = CustomerOrder.objects.create(
                    customer=customer_profile,
                    order_number=order_number,
                    shipping_address_id=serializer.validated_data['shipping_address_id'],
                    payment_method=serializer.validated_data['payment_method']
                )
                
                # Add items to order
                total_amount = 0
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product_id=cart_item.product_id,
                        product_name=cart_item.product_name,
                        product_image=cart_item.product_image,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product_price,
                        total_price=cart_item.total_price
                    )
                    total_amount += cart_item.total_price
                
                # Apply coupon if provided
                coupon_code = serializer.validated_data.get('coupon_code')
                if coupon_code:
                    try:
                        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                        if coupon.is_valid and total_amount >= coupon.minimum_amount:
                            if coupon.coupon_type == 'percentage':
                                discount = (total_amount * coupon.value) / 100
                                if coupon.maximum_discount:
                                    discount = min(discount, coupon.maximum_discount)
                            else:
                                discount = coupon.value
                            
                            order.discount_amount = discount
                            coupon.used_count += 1
                            coupon.save()
                    except Coupon.DoesNotExist:
                        pass
                
                # Calculate final total
                order.total_amount = total_amount - order.discount_amount
                order.save()
                
                # Clear cart
                cart.items.all().delete()
                
                # Create payment record
                Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method=order.payment_method
                )
                
                return Response({
                    'order_id': order.id,
                    'order_number': order.order_number, 
                    'message': 'Order created successfully'
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return Response(
                {'error': 'Failed to create order'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payment processing with mock payment gateway"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        return Payment.objects.filter(order__customer=customer_profile)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def process_payment(self, request):
        """Process mock payment for an order"""
        try:
            order_id = request.data.get('order_id')
            payment_method = request.data.get('payment_method', 'upi')
            
            if not order_id:
                return Response(
                    {'error': 'order_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            order = get_object_or_404(CustomerOrder, id=order_id, customer=customer_profile)
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(order=order).first()
            if existing_payment and existing_payment.payment_status == 'completed':
                return Response(
                    {'error': 'Payment already processed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mock payment processing
            import time
            import random
            time.sleep(2)  # Simulate processing time
            
            # Simulate payment success (90% success rate for demo)
            is_successful = random.random() < 0.9
            
            if existing_payment:
                payment = existing_payment
            else:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    payment_method=payment_method
                )
            
            if is_successful:
                payment.payment_status = 'completed'
                payment.paid_at = timezone.now()
                payment.gateway_transaction_id = f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
                payment.gateway_response = {
                    'status': 'success',
                    'transaction_id': payment.gateway_transaction_id,
                    'message': 'Payment processed successfully'
                }
                payment.save()
                
                # Update order status
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.save()
                
                return Response({
                    'message': 'Payment processed successfully',
                    'transaction_id': payment.gateway_transaction_id,
                    'status': 'success',
                    'order_number': order.order_number
                })
            else:
                payment.payment_status = 'failed'
                payment.gateway_response = {
                    'status': 'failed',
                    'message': 'Payment failed - insufficient funds'
                }
                payment.save()
                
                return Response({
                    'error': 'Payment failed - insufficient funds',
                    'status': 'failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return Response(
                {'error': 'Failed to process payment'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )