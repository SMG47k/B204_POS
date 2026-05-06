from django import forms
from .models import OrderItem

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ប្តូរការបង្ហាញក្នុង Dropdown ឱ្យមានឈ្មោះ តម្លៃ និងចំនួនស្តុក
        self.fields['product'].label_from_instance = lambda obj: f"{obj.name} — ${obj.price} (ស្តុក: {obj.stock})"
        
        # បន្ថែមការផ្ទៀងផ្ទាត់ថាចំនួនត្រូវតែចាប់ពី ១ ឡើង (ដូចក្នុង image_1e9701.jpg)
        self.fields['quantity'].widget.attrs.update({'min': '1'})
# sales/forms.py
from .models import Discount # ត្រូវប្រាកដថាមាន line នេះនៅខាងលើគេ

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'ឧ. បញ្ចុះតម្លៃបុគ្គលិក...', 'style': 'width: 100%; padding: 8px;'}),
            'amount': forms.NumberInput(attrs={'style': 'width: 100%; padding: 8px;', 'step': '0.01'}),
        }