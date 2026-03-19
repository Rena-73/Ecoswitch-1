#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoswitch_backend.settings')
django.setup()

from ecommerce.models import Product, Category, Brand
from decimal import Decimal

# Create categories
category, created = Category.objects.get_or_create(
    name="Fashion & Accessories",
    defaults={'slug': 'fashion-accessories', 'description': 'Eco-friendly fashion items'}
)

# Create brand
brand, created = Brand.objects.get_or_create(
    name="EcoStyle",
    defaults={'slug': 'ecostyle', 'description': 'Sustainable fashion brand'}
)

# Create sample products
products_data = [
    {
        'name': 'Organic Cotton Tote Bag',
        'slug': 'organic-cotton-tote-bag',
        'description': 'Eco-friendly cotton tote bag perfect for shopping and daily use',
        'short_description': 'Sustainable cotton tote bag',
        'category': category,
        'brand': brand,
        'sku': 'ECTB001',
        'price': Decimal('299.00'),
        'stock_quantity': 50,
        'eco_rating': 5,
        'is_organic': True,
        'is_biodegradable': True,
        'is_recyclable': True,
        'is_plastic_free': True,
        'carbon_footprint': Decimal('0.3'),
        'is_active': True,
        'is_featured': True
    },
    {
        'name': 'Reusable Water Bottle',
        'slug': 'reusable-water-bottle',
        'description': 'Stainless steel water bottle with bamboo cap - perfect for daily hydration',
        'short_description': 'Stainless steel water bottle with bamboo cap',
        'category': category,
        'brand': brand,
        'sku': 'RWB001',
        'price': Decimal('599.00'),
        'stock_quantity': 30,
        'eco_rating': 5,
        'is_organic': False,
        'is_biodegradable': False,
        'is_recyclable': True,
        'is_plastic_free': True,
        'carbon_footprint': Decimal('0.1'),
        'is_active': True,
        'is_featured': True
    },
    {
        'name': 'LED Solar Garden Lights',
        'slug': 'led-solar-garden-lights',
        'description': 'Set of 6 solar-powered LED garden lights with automatic dusk-to-dawn operation',
        'short_description': 'Solar-powered LED garden lights',
        'category': category,
        'brand': brand,
        'sku': 'LSGL001',
        'price': Decimal('899.00'),
        'stock_quantity': 25,
        'eco_rating': 5,
        'is_organic': False,
        'is_biodegradable': False,
        'is_recyclable': True,
        'is_plastic_free': False,
        'carbon_footprint': Decimal('0.15'),
        'is_active': True,
        'is_featured': False
    }
]

for product_data in products_data:
    product, created = Product.objects.get_or_create(
        sku=product_data['sku'],
        defaults=product_data
    )
    if created:
        print(f"Created product: {product.name}")
    else:
        print(f"Product already exists: {product.name}")

print(f"Total products in database: {Product.objects.count()}")
print("Database populated successfully!")
