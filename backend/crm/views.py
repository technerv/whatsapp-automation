from django.http import JsonResponse
from .models import Customer, Lead
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets
from .serializers import CustomerSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save(business=self.request.user.business)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    business = request.user.business
    customer_count = Customer.objects.filter(business=business).count()
    lead_count = Lead.objects.filter(business=business).count()
    # Add more stats as we build out the features

    data = {
        'customer_count': customer_count,
        'lead_count': lead_count,
    }
    return JsonResponse(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_signups(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    business = request.user.business

    daily_data = []
    for i in range(8):
        date = seven_days_ago + timedelta(days=i)
        customer_count = Customer.objects.filter(business=business, created_at__date=date).count()
        lead_count = Lead.objects.filter(business=business, created_at__date=date).count()
        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'customers': customer_count,
            'leads': lead_count,
        })

    return JsonResponse(daily_data, safe=False)