from django.urls import path
from rest_framework.urls import app_name


from analytics.views import AnalyticsPageView, AnalyticsView, ExportCSVView, ExportPDFView, TopExpenseCategoriesView, \
    IncomeExpenseTrendView, income_expense_trend_chart

app_name = 'analytics'
urlpatterns = [
    path('analytics-page/', AnalyticsPageView.as_view(), name='analytics_page'),
    path('analytics/', AnalyticsView.as_view(), name='analytics_api'),
    path('top-expenses/', TopExpenseCategoriesView.as_view(), name='top_expenses'),
    path('export-csv/', ExportCSVView.as_view(), name='export_csv'),
    path('export-pdf/', ExportPDFView.as_view(), name='export-pdf'),
    path('top-expenses/', TopExpenseCategoriesView.as_view(), name='top-expenses'),
    path('trend/', IncomeExpenseTrendView.as_view(), name='income_expense_trend'),
    path('trend-chart/', income_expense_trend_chart, name='trend_chart'),
]