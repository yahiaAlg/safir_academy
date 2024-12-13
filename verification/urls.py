from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('scanner/', views.scanner, name='scanner'),
    path('manual-search/', views.manual_search, name='manual_search'),
    
    
    path('verify-qr/', views.verify_qr, name='verify_qr'),  # Updated to match the request URL
    
    path('verification-result/<str:reg_id>/', views.verification_result, name='verification_result'),
    # path('result/<uuid:reg_id>/', views.verification_result, name='verification_result'),
    path('dashboard/', views.dashboard, name='dashboard'),
]