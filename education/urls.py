from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.education, name='education'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('delete/<slug:slug>/', views.delete_lesson, name='delete_lesson'),
    path('compound-interest/', views.compound_interest, name='compound_interest'),
    path('tradeoasis/', views.tradeoasis, name='tradeoasis'),
    path('snp500/', views.snp500, name='snp500'),
    path('<slug:slug>/', views.lesson_detail, name='lesson_detail'),
]