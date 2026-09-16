from rest_framework import viewsets
from .models import Supplier
from .serializers import SupplierSerializer
from rest_framework.permissions import IsAuthenticated

class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Supplier.objects.filter(business__in=self.request.user.businesses.all())

    def perform_create(self, serializer):
        # TODO: Associate with a business from the user's businesses
        pass