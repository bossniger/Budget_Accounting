from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import frontend_urls
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'users', UserViewSet)
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'counterparties', CounterpartyViewSet, basename='counterparties')

urlpatterns = [
    # API маршруты
    path('v1/', include(router.urls)),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('analytics/', include('analytics.urls')),
    # Маршруты для HTML-страниц
    path('', include(frontend_urls)),
]