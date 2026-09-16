from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    OnboardingView,
    CurrentUserView,
    BusinessView,
    UserUpdateView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('me/', CurrentUserView.as_view(), name='me'),
    path('me/update/', UserUpdateView.as_view(), name='me-update'),
    path('business/', BusinessView.as_view(), name='business'),
]