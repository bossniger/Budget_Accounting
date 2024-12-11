from datetime import datetime

import django
from Tools.demo.mcast import sender
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Sum, Case, When, DecimalField

from .docs.budget_docs import BUDGET_LIST_RESPONSE, BUDGET_CREATE_EXAMPLE, BUDGET_CREATE_RESPONSE
from .docs.category_docs import CATEGORY_FILTER_PARAMS, CATEGORY_LIST_RESPONSE, CATEGORY_CREATE_RESPONSE
from .docs.transaction_docs import TRANSACTION_FILTER_PARAMS, TRANSACTION_LIST_RESPONSE
from .filters import TransactionFilter
from .models import Transaction, Category, Tag, Budget
from .serializers import *
from rest_framework.permissions import IsAuthenticated


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['date', 'amount']  # Поля для сортировки
    ordering = ['-date']
    @swagger_auto_schema(
        operation_description='Получение списка транзакций с фильтрацие и сортировкой',
        manual_parameters=TRANSACTION_FILTER_PARAMS,
        responses={200: TRANSACTION_LIST_RESPONSE}
    )
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение списка категорий",
        manual_parameters=CATEGORY_FILTER_PARAMS,
        responses={200: CATEGORY_LIST_RESPONSE}
    )
    def list(self, request, *args, **kwargs):
        """
        Список категорий с фильтрацией по названию.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание новой категории",
        responses={201: CATEGORY_CREATE_RESPONSE}
    )
    def create(self, request, *args, **kwargs):
        """
        Создание категории.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о категории по ID",
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получение одной категории по ID.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновление категории по ID",
    )
    def update(self, request, *args, **kwargs):
        """
        Обновление категории.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление категории по ID",
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление категории.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление категории по ID",
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удаление категории.
        """
        return super().destroy(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    #permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]


class TransferView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # Обновление балансов происходит в модели Transfer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=Transaction)
def check_budget_limit(sender, instance, **kwargs):
    if instance.type == 'expense':
        budgets = Budget.objects.filter(
            user=instance.user,
            category=instance.category,
            start_date__lte=instance.date,
            end_date__gte=instance.date
        )
        for budget in budgets:
            total_expenses = Transaction.objects.filter(
                user=instance.user,
                category=instance.category,
                type='expense',
                date__range=(budget.start_date, budget.end_date)
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or 0
            if total_expenses > budget.amount:
                # Логика для уведомления
                print(f"Бюджет для категории {budget.category.name} превышен!")


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Budget.objects.all()

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получение списка бюджетов текущего пользователя",
        responses={200: BUDGET_LIST_RESPONSE},
    )
    def list(self, request, *args, **kwargs):
        """
        Возвращает список всех бюджетов текущего пользователя.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание нового бюджета",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "category": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID категории"),
                "amount": openapi.Schema(type=openapi.TYPE_STRING, format="decimal", description="Сумма бюджета"),
                "start_date": openapi.Schema(type=openapi.FORMAT_DATE, description="Дата начала бюджета"),
                "end_date": openapi.Schema(type=openapi.FORMAT_DATE, description="Дата окончания бюджета"),
            },
            required=["category", "amount", "start_date", "end_date"],
            example=BUDGET_CREATE_EXAMPLE,
        ),
        responses={201: BUDGET_CREATE_RESPONSE},
    )
    def create(self, request, *args, **kwargs):
        """
        Создает новый бюджет для текущего пользователя.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Получение информации о бюджете по ID")
    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает информацию о конкретном бюджете по ID.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Полное обновление бюджета по ID")
    def update(self, request, *args, **kwargs):
        """
        Полное обновление информации о бюджете.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Частичное обновление бюджета по ID")
    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление информации о бюджете.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Удаление бюджета по ID")
    def destroy(self, request, *args, **kwargs):
        """
        Удаление бюджета.
        """
        return super().destroy(request, *args, **kwargs)
