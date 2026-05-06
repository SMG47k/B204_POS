# sales/admin.py

from django.contrib import admin
from .models import Product, Order, OrderItem, Discount  # ← បន្ថែម Discount ត្រង់នេះ


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'stock', 'is_active']
    list_filter   = ['category', 'is_active']
    search_fields = ['name', 'barcode']
    ordering      = ['name']


class OrderItemInline(admin.TabularInline):
    """បង្ហាញ order items ផ្ទាល់នៅក្នុងទំព័រកែ Order"""
    model  = OrderItem
    extra  = 1    # ចំនួនជួរទទេដែលបង្ហាញសម្រាប់បន្ថែម items ថ្មី
    fields = ['product', 'quantity', 'unit_price']


# បង្កើត Inline សម្រាប់ Discount ដើម្បីឱ្យវាបង្ហាញក្នុងទំព័រ Order តែម្តង
class DiscountInline(admin.StackedInline):
    model = Discount
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'cashier', 'status', 'total', 'created_at']  # ← ថែម 'total' ដើម្បីមើលតម្លៃសរុប
    list_filter   = ['status']
    search_fields = ['cashier', 'notes']
    ordering      = ['-created_at']
    inlines       = [OrderItemInline, DiscountInline]    # ← បន្ថែម DiscountInline ទៅក្នុងបញ្ជី


# ចុះឈ្មោះ Discount ជា Model ដាច់ដោយឡែក (ជម្រើសបន្ថែម)
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'order']