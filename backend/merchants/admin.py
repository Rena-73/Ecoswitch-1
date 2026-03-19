from django.contrib import admin
from .models import Store, MerchantProfile, MerchantProduct, MerchantOrder, OrderItem, MerchantAnalytics


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'merchant', 'city', 'state', 'country', 'created_at')
    list_filter = ('city', 'state', 'country', 'created_at')
    search_fields = ('store_name', 'merchant__business_name', 'street_address', 'city', 'state')
    raw_id_fields = ('merchant',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'business_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('business_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('business_name', 'user__email', 'contact_person')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MerchantProduct)
class MerchantProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'category', 'price', 'stock_quantity', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'is_eco_friendly', 'created_at')
    search_fields = ('name', 'merchant__business_name', 'brand', 'sku')
    raw_id_fields = ('merchant',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MerchantOrder)
class MerchantOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'merchant', 'customer_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'merchant', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'merchant__business_name')
    raw_id_fields = ('merchant',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__merchant', 'order__created_at')
    search_fields = ('product__name', 'order__order_number')
    raw_id_fields = ('product', 'order')


@admin.register(MerchantAnalytics)
class MerchantAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'date', 'total_orders', 'total_revenue', 'average_order_value')
    list_filter = ('date', 'merchant')
    search_fields = ('merchant__business_name',)
    raw_id_fields = ('merchant',)
    readonly_fields = ('created_at',)

















