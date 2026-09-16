from rest_framework import serializers
from .models import Product, Category, Inventory

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'business', 'category', 'name', 'description', 'sku', 'price',
                  'quantity', 'low_stock_threshold', 'created_at', 'updated_at')
        read_only_fields = ('id', 'business', 'created_at', 'updated_at')

    def validate_category(self, category):
        business = self.context['request'].user.business
        if category and category.business_id != business.id:
            raise serializers.ValidationError('Category must belong to your business.')
        return category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'business', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'business', 'created_at', 'updated_at')

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'product', 'quantity', 'updated_at')
        read_only_fields = ('id', 'updated_at')

    def validate_product(self, product):
        business = self.context['request'].user.business
        if product.business_id != business.id:
            raise serializers.ValidationError('Product must belong to your business.')
        return product