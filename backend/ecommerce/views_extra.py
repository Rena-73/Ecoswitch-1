from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid
import logging

from .models import Coupon, Payment, ShippingMethod, OrderTracking, EcoImpact
from .serializers import (
    CustomerOrderSerializer, CreateOrderSerializer, CouponSerializer, 
    PaymentSerializer, ShippingMethodSerializer, OrderTrackingSerializer, 
    EcoImpactSerializer, WishlistItemSerializer, AddToWishlistSerializer
)
from customers.models import Cart, CartItem, CustomerProfile, CustomerOrder, OrderItem, CustomerWishlist
from .models import Product

logger = logging.getLogger(__name__)


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


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for wishlist management"""
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        return CustomerWishlist.objects.filter(customer=customer_profile)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_item(self, request):
        """Add item to wishlist"""
        try:
            serializer = AddToWishlistSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            customer_profile = get_object_or_404(CustomerProfile, user=request.user)
            product_id = serializer.validated_data['product_id']
            
            try:
                product = Product.objects.get(id=int(product_id), is_active=True)
            except (ValueError, Product.DoesNotExist):
                return Response(
                    {'error': 'Product not found or inactive'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            wishlist_item, created = CustomerWishlist.objects.get_or_create(
                customer=customer_profile,
                product_id=product_id,
                defaults={
                    'product_name': product.name,
                    'product_image': self._get_product_image_url(product),
                    'product_price': product.price
                }
            )
            
            if created:
                return Response({
                    'message': 'Item added to wishlist successfully',
                    'item': WishlistItemSerializer(wishlist_item).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Item already in wishlist',
                    'item': WishlistItemSerializer(wishlist_item).data
                })
                
        except Exception as e:
            logger.error(f"Error adding item to wishlist: {str(e)}")
            return Response(
                {'error': 'Failed to add item to wishlist'}, 
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


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for coupons (read-only)"""
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for shipping methods (read-only)"""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]


class EcoImpactViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for eco impact tracking (read-only)"""
    serializer_class = EcoImpactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EcoImpact.objects.filter(user=self.request.user)


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