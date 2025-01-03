from django.urls import path
from rest_framework.urls import app_name

from analytics.views import AnalyticsPageView, AnalyticsView, ExportCSVView, ExportPDFView

app_name = 'analytics'
urlpatterns = [
    path('analytics-page/', AnalyticsPageView.as_view(), name='analytics_page'),
    path('analytics/', AnalyticsView.as_view(), name='analytics_api'),
    path('export-csv/', ExportCSVView.as_view(), name='export_csv'),
    path('export-pdf/', ExportPDFView.as_view(), name='export-pdf')
]