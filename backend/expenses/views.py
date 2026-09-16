from rest_framework import viewsets
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
from rest_framework.permissions import IsAuthenticated

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(business__in=self.request.user.businesses.all())

    def perform_create(self, serializer):
        # TODO: Associate with a business from the user's businesses
        pass

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExpenseCategory.objects.filter(business__in=self.request.user.businesses.all())

    def perform_create(self, serializer):
        # TODO: Associate with a business from the user's businesses
        pass