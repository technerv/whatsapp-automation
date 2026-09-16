from django.db import models
import uuid
from accounts.models import Business, User
from crm.models import Customer

class WhatsAppAccount(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='whatsapp_accounts')
    phone_number_id = models.CharField(max_length=100, unique=True)
    business_account_id = models.CharField(max_length=100, blank=True)
    display_phone_number = models.CharField(max_length=30, blank=True)
    access_token = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WebhookEvent(models.Model):
    STATUS_CHOICES = [('received', 'Received'), ('processed', 'Processed'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, default='whatsapp')
    external_event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)


class Conversation(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('pending', 'Pending'), ('closed', 'Closed')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='conversations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_conversations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    unread_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['business', 'customer'], name='unique_conversation_per_customer'),
        ]
        indexes = [
            models.Index(fields=['business', 'status', 'last_message_at']),
            models.Index(fields=['business', 'assigned_to']),
        ]

    def __str__(self):
        return f"Conversation with {self.customer}"

class WhatsAppMessage(models.Model):
    STATUS_CHOICES = [('queued', 'Queued'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read'), ('failed', 'Failed')]
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    whatsapp_message_id = models.CharField(max_length=255, unique=True)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    content = models.TextField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp', 'id']

    def __str__(self):
        return f"Message from {self.conversation.customer} at {self.timestamp}"