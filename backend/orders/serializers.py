from rest_framework import serializers
from django.db import transaction
from crm.models import Customer
from inventory.models import Product
from .models import Order, OrderItem, Invoice, Receipt

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total')
        read_only_fields = ('id', 'price', 'total')

    def validate_quantity(self, quantity):
        if quantity < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'business', 'customer', 'order_date', 'status', 'total_amount', 'created_by', 'items')
        read_only_fields = ('id', 'business', 'order_date', 'status', 'total_amount', 'created_by')

    def validate_customer(self, customer):
        business = self.context['request'].user.business
        if customer.business_id != business.id:
            raise serializers.ValidationError('Customer must belong to your business.')
        return customer

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('An order must contain at least one item.')
        business = self.context['request'].user.business
        product_ids = [item['product'].id for item in items]
        products = Product.objects.filter(business=business, id__in=product_ids)
        if products.count() != len(set(product_ids)):
            raise serializers.ValidationError('All products must belong to your business.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')
        request = self.context['request']
        business = request.user.business
        order = Order.objects.create(
            business=business,
            created_by=request.user,
            status=Order.STATUS_CHOICES[0][0],
            **validated_data,
        )
        total = 0
        for item_data in items:
            product = Product.objects.select_for_update().get(pk=item_data['product'].pk)
            quantity = item_data['quantity']
            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f'Insufficient stock for {product.name}.'
                )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                total=product.price * quantity,
            )
            product.quantity -= quantity
            product.save(update_fields=['quantity', 'updated_at'])
            total += product.price * quantity
        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'