from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_public_key, name='submit_key'),
    path('success/', views.success, name='success'),  # Страница успеха после отправки
]