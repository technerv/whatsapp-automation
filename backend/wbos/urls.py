"""
URL configuration for wbos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .health import healthz, readyz

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('readyz/', readyz, name='readyz'),
    path('admin/', admin.site.urls),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/suppliers/', include('suppliers.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/ai/', include('ai_automations.urls')),
    path('api/v1/crm/', include('crm.urls')),
    path('api/v1/', include('whatsapp.urls')),
    path('api/commerce/', include('commerce.urls')),
]