from django.urls import path
from . import views

urlpatterns = [
    path('', views.codes, name='codes'),
    path('students/', views.students, name='students'),
]
