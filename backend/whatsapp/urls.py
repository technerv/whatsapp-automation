from django.urls import path
from rest_framework_nested import routers
from .views import ConversationViewSet, WhatsAppMessageViewSet, whatsapp_webhook

router = routers.SimpleRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

conversations_router = routers.NestedSimpleRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', WhatsAppMessageViewSet, basename='conversation-messages')

urlpatterns = router.urls + conversations_router.urls + [
	path('webhooks/whatsapp/', whatsapp_webhook, name='whatsapp-webhook'),
]