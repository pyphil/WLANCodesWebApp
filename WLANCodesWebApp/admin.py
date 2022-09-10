from django.contrib import admin
from .models import Student



class StudentCustomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'firstname',
        'group',
        'email',
        'code',
        )
    list_filter = (
        'name',
        'firstname',
        'group',
        'email',
        'code',
        )

admin.site.register(Student, StudentCustomAdmin)