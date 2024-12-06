from django.urls import path, include

from analytics.views import AnalyticsPageView, AnalyticsView

urlpatterns = [
    path('analytics-page/', AnalyticsPageView.as_view(), name='analytics_page'),
    path('analytics/', AnalyticsView.as_view(), name='analytics_api'),
]