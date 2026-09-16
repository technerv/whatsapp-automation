from rest_framework.permissions import BasePermission

from .models import Membership


class HasBusinessMembership(BasePermission):
    """Allow access only to users with an active membership in the object's business."""

    def has_object_permission(self, request, view, obj):
        business_id = getattr(obj, 'business_id', None)
        if business_id is None:
            business_id = getattr(obj, 'business', None)
            business_id = getattr(business_id, 'pk', business_id)

        return Membership.objects.filter(
            business_id=business_id,
            user=request.user,
            status=Membership.Status.ACTIVE,
        ).exists()