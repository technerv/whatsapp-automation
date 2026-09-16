from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # TODO: Replace with real data
        data = {
            'total_sales': 10000,
            'total_customers': 100,
            'total_orders': 50,
            'total_products': 200,
        }
        return Response(data)