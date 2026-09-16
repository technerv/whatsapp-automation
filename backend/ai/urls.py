from django.urls import path
from .views import AssistantView

urlpatterns = [
    path('assistant/', AssistantView.as_view(), name='assistant'),
]