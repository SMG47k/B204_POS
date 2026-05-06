from django.db import models
from django.contrib.auth.models import User  # ← ចាំបាច់ត្រូវមានសម្រាប់កូដថ្មី

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'អាហារ និងភេសជ្ជៈ'),
        ('electronics', 'អេឡិចត្រូនិក'),
        ('clothing', 'សម្លៀកបំពាក់'),
        ('household', 'គ្រឿងសង្ហារឹម'),
        ('other', 'ផ្សេងៗ'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — ${self.price} (ស្តុក: {self.stock})"

    class Meta:
        ordering = ['name']

class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    # ប្តូរពី CharField ទៅជា ForeignKey ដើម្បីភ្ជាប់ទៅកាន់ User ដែលបាន Login
    cashier = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    @property
    def total(self):
        # គណនាតម្លៃសរុបដោយបូក subtotal ពីគ្រប់ OrderItem ទាំងអស់
        subtotal = sum(item.subtotal for item in self.items.all())
        try:
            return subtotal - self.discount.amount
        except:
            return subtotal

    def __str__(self):
        name = self.cashier.username if self.cashier else 'unknown'
        return f"Order #{self.pk} [{self.status.upper()}] by {name} — ${self.total:.2f}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.name} @ ${self.unit_price}"

class Discount(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='discount')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.description} (-${self.amount}) នៅការបញ្ជាទិញ #{self.order.pk}"