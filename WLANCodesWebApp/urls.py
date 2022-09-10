from django.urls import path
from . import views

urlpatterns = [
    path('', views.codes, name='codes'),
    path('new_student/', views.new_student, name='new_student'),
    path('students/', views.students, name='students'),
    path('student_import/', views.student_import, name='student_import'),
]
