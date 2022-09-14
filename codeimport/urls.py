from django.urls import path
from . import views

urlpatterns = [
    path('', views.codeimport, name='codeimport'),
]