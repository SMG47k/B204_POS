# sales/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Product, Order, OrderItem, Discount
from .forms import OrderItemForm, DiscountForm # ត្រូវប្រាកដថាបានបន្ថែម DiscountForm ក្នុង forms.py រួចហើយ

@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # គណនាតួលេខសម្រាប់ Dashboard (ដូចរូបភាព image_1e975a.jpg)
    total_orders = orders.count()
    total_revenue = sum(o.total for o in orders if o.status == 'paid')
    completed_orders = orders.filter(status='paid').count()
    discounted_orders = orders.filter(discount__isnull=False).count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'completed_orders': completed_orders,
        'discounted_orders': discounted_orders,
    }
    return render(request, 'sales/order_list.html', context)

@login_required
def create_order(request):
    """បង្កើតវិក្កយបត្រថ្មីភ្លាមៗ"""
    order = Order.objects.create(
        cashier=request.user,
        status='open',
    )
    return redirect('add_item', pk=order.pk)

@login_required
def add_item(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # បញ្ឈប់ការកែប្រែបើវិក្កយបត្របិទរួចហើយ
    if order.status != 'open':
        return redirect('order_list')

    if request.method == 'POST':
        # ១. បើចុចប៊ូតុង "បង់ប្រាក់"
        if 'mark_paid' in request.POST:
            order.status = 'paid'
            order.save()
            return redirect('order_list')
        
        # ២. បើចុចប៊ូតុង "Cancel Order" (ដូចរូបភាព image_1e971d.jpg)
        if 'cancel_order' in request.POST:
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
            order.status = 'cancelled'
            order.save()
            return redirect('order_list')

        # ៣. មុខងារបញ្ចុះតម្លៃ (ដូចរូបភាព image_1e9738.jpg)
        if 'apply_discount' in request.POST:
            discount_form = DiscountForm(request.POST)
            if discount_form.is_valid():
                # លុប discount ចាស់ចេញ រួចបញ្ចូលអាថ្មី
                Discount.objects.filter(order=order).delete()
                discount = discount_form.save(commit=False)
                discount.order = order
                discount.save()
            return redirect('add_item', pk=order.pk)

        # ៤. ការបន្ថែមទំនិញ (Add Item)
        item_form = OrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            if item.product.stock >= item.quantity:
                item.order = order
                item.unit_price = item.product.price
                item.save()
                item.product.stock -= item.quantity
                item.product.save()
            return redirect('add_item', pk=order.pk)
            
    else:
        item_form = OrderItemForm()
        # បង្កើត Discount Form ទទេរ (ដូចរូបភាព image_1e9738.jpg)
        discount_form = DiscountForm()

    return render(request, 'sales/add_item.html', {
        'order': order,
        'item_form': item_form,
        'discount_form': discount_form, # បញ្ជូន Form ទៅកាន់ HTML
        'items': order.items.select_related('product'),
    })