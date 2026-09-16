from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AutomationEventView, DialogflowWebhook, WorkflowViewSet

router = DefaultRouter()
router.register('workflows', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('dialogflow-webhook/', DialogflowWebhook.as_view(), name='dialogflow-webhook'),
    path('automation/events/', AutomationEventView.as_view(), name='automation-event'),
    path('', include(router.urls)),
]