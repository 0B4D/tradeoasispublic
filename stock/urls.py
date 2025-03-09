from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_home, name='stock_home'),
    # URL pattern for a specific stock (e.g., /stock/AAPL/)
    path('<str:ticker>/', views.stock_detail, name='stock_detail'),
    path('<str:ticker>/data/', views.stock_data, name='stock_data'),
]