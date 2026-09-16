from django.contrib import admin
from .models import Order, OrderItem, Invoice, Receipt

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Invoice)
admin.site.register(Receipt)