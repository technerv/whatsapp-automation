from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='inventory-product')
router.register(r'categories', CategoryViewSet, basename='inventory-category')
router.register(r'inventory', InventoryViewSet, basename='inventory-record')

urlpatterns = [
    path('', include(router.urls)),
]