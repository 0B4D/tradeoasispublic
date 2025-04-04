from django.urls import path, include
from . import views

app_name = 'stock_hr'

urlpatterns = [
    path('stock/', views.stock_home_hr, name='stock_home'),
    path('index/', views.indexes, name='index'),
    path('<str:asset_type>/<str:asset_name>', views.asset_detail_hr, name='asset_detail_hr'),
]