from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='categories/category_list.html'), name='category_list'),
]