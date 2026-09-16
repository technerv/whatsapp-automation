from django.contrib import admin
from .models import AutomationEvent, AutomationLog, Workflow, WorkflowExecution

admin.site.register(Workflow)
admin.site.register(AutomationEvent)
admin.site.register(WorkflowExecution)
admin.site.register(AutomationLog)
