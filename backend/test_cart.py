#!/usr/bin/env python
"""
Test script to verify cart functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoswitch_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from customers.models import CustomerProfile, Cart, CartItem
from ecommerce.models import Product

User = get_user_model()

def test_cart_functionality():
    print("Testing cart functionality...")
    
    # Check if there are products
    product_count = Product.objects.count()
    print(f"Products in database: {product_count}")
    
    if product_count == 0:
        print("No products found. Please run the populate script first.")
        return
    
    # Get the first product
    product = Product.objects.first()
    print(f"Testing with product: {product.name} (ID: {product.id})")
    
    # Check if there are any users
    user_count = User.objects.count()
    print(f"Users in database: {user_count}")
    
    if user_count == 0:
        print("No users found. Please create a user first.")
        return
    
    # Get the first user
    user = User.objects.first()
    print(f"Testing with user: {user.email} (Type: {user.user_type})")
    
    # Check if customer profile exists
    try:
        customer_profile = CustomerProfile.objects.get(user=user)
        print(f"Customer profile exists: {customer_profile}")
    except CustomerProfile.DoesNotExist:
        print("Creating customer profile...")
        customer_profile = CustomerProfile.objects.create(user=user)
        print(f"Customer profile created: {customer_profile}")
    
    # Test cart creation
    cart, created = Cart.objects.get_or_create(customer=customer_profile)
    print(f"Cart {'created' if created else 'retrieved'}: {cart}")
    
    # Test adding item to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=str(product.id),
        defaults={
            'product_name': product.name,
            'product_image': '',
            'product_price': product.price,
            'quantity': 1
        }
    )
    
    if created:
        print(f"Cart item created: {cart_item}")
    else:
        print(f"Cart item already exists: {cart_item}")
    
    # Test cart retrieval
    cart_items = CartItem.objects.filter(cart=cart)
    print(f"Cart items count: {cart_items.count()}")
    
    for item in cart_items:
        print(f"  - {item.product_name}: {item.quantity} x ₹{item.product_price}")
    
    print("Cart functionality test completed successfully!")

if __name__ == "__main__":
    test_cart_functionality()
