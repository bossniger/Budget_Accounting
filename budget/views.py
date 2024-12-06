from datetime import datetime
from turtledemo.penrose import start

from django.db.models import Sum, Case, When, DecimalField
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction, Category, Tag
from .serializers import *
from rest_framework.permissions import IsAuthenticated


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [IsAuthenticated]


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
