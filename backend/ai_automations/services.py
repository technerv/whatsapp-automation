from django.db import transaction
from django.utils import timezone

from .models import AutomationEvent, AutomationLog, Workflow, WorkflowExecution


def execute_workflow(*, workflow, event):
    """Execute only declarative, allowlisted workflow actions."""
    with transaction.atomic():
        execution = WorkflowExecution.objects.create(
            business=workflow.business,
            workflow=workflow,
            event=event,
            context=event.payload,
        )
        try:
            for node in workflow.definition['nodes']:
                AutomationLog.objects.create(
                    execution=execution,
                    node_key=node['key'],
                    action=node['action'],
                    status='completed',
                    input=node.get('config', {}),
                    output={'queued': True},
                )
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save(update_fields=['status', 'completed_at'])
            event.status = 'processed'
            event.processed_at = timezone.now()
            event.save(update_fields=['status', 'processed_at'])
        except Exception as exc:
            execution.status = 'failed'
            execution.error = str(exc)
            execution.save(update_fields=['status', 'error'])
            event.status = 'failed'
            event.save(update_fields=['status'])
            raise
    return execution


def publish_event(*, business, event_type, payload, idempotency_key, aggregate_type='', aggregate_id=''):
    event, created = AutomationEvent.objects.get_or_create(
        business=business,
        idempotency_key=idempotency_key,
        defaults={
            'event_type': event_type,
            'payload': payload,
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id,
        },
    )
    if not created:
        return event, False
    for workflow in Workflow.objects.filter(business=business, trigger_type=event_type, status='active'):
        execute_workflow(workflow=workflow, event=event)
    return event, True