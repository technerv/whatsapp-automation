from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter
from .views import CustomerViewSet

router = SimpleRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('daily-signups/', views.daily_signups, name='daily-signups'),
] + router.urls