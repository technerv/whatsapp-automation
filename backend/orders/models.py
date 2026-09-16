from django.db import models
from django.db.models import Q
import uuid

from accounts.models import Business, User
from crm.models import Customer
from inventory.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('pending_confirmation', 'Pending confirmation'),
        ('awaiting_payment', 'Awaiting payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('ready_for_delivery', 'Ready for delivery'),
        ('out_for_delivery', 'Out for delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    ALLOWED_TRANSITIONS = {
        'new': {'pending_confirmation', 'cancelled'},
        'pending_confirmation': {'awaiting_payment', 'cancelled'},
        'awaiting_payment': {'paid', 'cancelled'},
        'paid': {'processing', 'refunded'},
        'processing': {'ready_for_delivery', 'cancelled'},
        'ready_for_delivery': {'out_for_delivery'},
        'out_for_delivery': {'delivered'},
        'delivered': set(),
        'cancelled': set(),
        'refunded': set(),
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')

    def __str__(self):
        return f"Order {self.id} for {self.customer}"

    def transition_to(self, new_status):
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f'Unknown order status: {new_status}')
        if new_status not in self.ALLOWED_TRANSITIONS.get(self.status, set()):
            raise ValueError(f'Cannot transition order from {self.status} to {new_status}')
        self.status = new_status


class Cart(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('converted', 'Converted'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='carts')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='carts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'customer'],
                condition=Q(status='active'),
                name='unique_active_cart_per_customer',
            ),
        ]

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), 0)


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_product_per_cart'),
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Invoice for Order {self.order.id}"

class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='receipts')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50) # e.g., 'M-Pesa', 'Cash', 'Bank Transfer'
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # For M-Pesa, etc.

    def __str__(self):
        return f"Receipt for Invoice {self.invoice.id}"