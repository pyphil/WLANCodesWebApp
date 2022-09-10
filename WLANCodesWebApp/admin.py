from django.contrib import admin
from .models import Student



class StudentCustomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'firstname',
        'group',
        'email',
        'date',
        'code',
        )
    list_filter = (
        'name',
        'firstname',
        'group',
        'email',
        'date',
        'code',
        )

admin.site.register(Student, StudentCustomAdmin)