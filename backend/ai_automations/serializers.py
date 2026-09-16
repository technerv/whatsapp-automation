from rest_framework import serializers

from .models import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ('id', 'business', 'name', 'trigger_type', 'definition', 'status', 'version',
                  'created_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'business', 'status', 'version', 'created_by', 'created_at', 'updated_at')

    def validate_definition(self, definition):
        nodes = definition.get('nodes') if isinstance(definition, dict) else None
        if not isinstance(nodes, list) or not nodes:
            raise serializers.ValidationError('definition.nodes must be a non-empty list.')
        allowed = {'send_whatsapp_message', 'add_contact_tag', 'assign_conversation', 'wait', 'condition'}
        for node in nodes:
            if not isinstance(node, dict) or not node.get('key') or node.get('action') not in allowed:
                raise serializers.ValidationError('Each node needs a key and an allowed action.')
        return definition