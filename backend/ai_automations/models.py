import uuid

from django.db import models

from accounts.models import Business, User


class Workflow(models.Model):
	STATUS_CHOICES = [('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused')]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='workflows')
	name = models.CharField(max_length=255)
	trigger_type = models.CharField(max_length=100)
	definition = models.JSONField(default=dict)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	version = models.PositiveIntegerField(default=1)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='workflows')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['business', 'name'], name='unique_workflow_name_per_business'),
		]
		ordering = ['name', 'id']


class AutomationEvent(models.Model):
	STATUS_CHOICES = [('received', 'Received'), ('processed', 'Processed'), ('failed', 'Failed')]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='automation_events')
	event_type = models.CharField(max_length=100)
	aggregate_type = models.CharField(max_length=100, blank=True)
	aggregate_id = models.CharField(max_length=100, blank=True)
	payload = models.JSONField(default=dict)
	idempotency_key = models.CharField(max_length=255)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
	created_at = models.DateTimeField(auto_now_add=True)
	processed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['business', 'idempotency_key'], name='unique_automation_event_per_business'),
		]


class WorkflowExecution(models.Model):
	STATUS_CHOICES = [('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='workflow_executions')
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
	event = models.ForeignKey(AutomationEvent, on_delete=models.CASCADE, related_name='executions')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
	context = models.JSONField(default=dict)
	error = models.TextField(blank=True)
	started_at = models.DateTimeField(auto_now_add=True)
	completed_at = models.DateTimeField(null=True, blank=True)


class AutomationLog(models.Model):
	execution = models.ForeignKey(WorkflowExecution, on_delete=models.CASCADE, related_name='logs')
	node_key = models.CharField(max_length=100)
	action = models.CharField(max_length=100)
	status = models.CharField(max_length=20)
	input = models.JSONField(default=dict)
	output = models.JSONField(default=dict)
	error = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
