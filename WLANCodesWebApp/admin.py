from django.contrib import admin
from .models import Student



class StudentCustomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'firstname',
        'group',
        'code',
        )
    list_filter = (
        'name',
        'firstname',
        'group',
        'code',
        )

admin.site.register(Student, StudentCustomAdmin)