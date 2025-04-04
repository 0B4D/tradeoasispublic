"""
URL configuration for tradeoasis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'tradeoasis'

urlpatterns = [
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("test/", views.testing),
    path('stock/', include('stock.urls')),
    path('accounts/', include('accounts.urls')),
    path('interest_calculator/', views.interest_calculator, name='interest_calculator'),
    path('education/', include('education.urls')),
    path('help/', views.help, name='help'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('accinfo/', views.account_info, name='account_info'),
    path('stock_hr/', include('stock_hr.urls')),
    path('account/reset-portfolio/', views.reset_portfolio, name='reset_portfolio')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
