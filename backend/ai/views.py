from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json

class AssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt', '').lower()

        # Mock AI responses based on keywords in the prompt
        if 'sales' in prompt:
            response_data = {
                'response': "Based on your recent sales data, you have a 20% increase in sales this month. Keep up the great work!",
                'data': {'sales_increase': '20%'}
            }
        elif 'customers' in prompt:
            response_data = {
                'response': "You have acquired 5 new customers this week. Consider sending them a welcome message.",
                'data': {'new_customers': 5}
            }
        elif 'inventory' in prompt:
            response_data = {
                'response': "Your stock of 'Product X' is running low. You have 10 units left. Would you like to reorder?",
                'data': {'low_stock_product': 'Product X', 'units_left': 10}
            }
        else:
            response_data = {
                'response': "I'm sorry, I can't help with that right now. I am still under development. Please try asking about sales, customers, or inventory.",
                'data': {}
            }

        return Response(response_data)