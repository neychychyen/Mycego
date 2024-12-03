from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_public_key, name='submit_key'),
    path('success/', views.success, name='success'),  # Страница успеха после отправки

    # ajax
    path('success/ajax_status/', views.ajax_isAvailable, name='ajax_status'),
    path('success/ajax_elements/', views.ajax_get_elements, name='ajax_elements'),

    #download
    path('success/download/', views.download_file, name='download_file')
]