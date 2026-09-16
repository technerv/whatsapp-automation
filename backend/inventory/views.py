from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Product, Category, Inventory
from .serializers import ProductSerializer, CategorySerializer, InventorySerializer
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(business=self.request.user.business).select_related('category')

    def perform_create(self, serializer):
        self._require_business()
        serializer.save(business=self.request.user.business)

    def _require_business(self):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save(business=self.request.user.business)

class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inventory.objects.filter(product__business=self.request.user.business).select_related('product')

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save()