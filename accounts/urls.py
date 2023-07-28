from django.urls import path
from . import views


# /accounts/...
urlpatterns = [
    path('register/<str:uuid>/', views.register, name='register'),
    path('email_check/', views.email_check, name='email_check'),
    path('registation_email/', views.registration_email, name='registration_email'),
    path('account_success/', views.account_success, name='account_success'),
]
