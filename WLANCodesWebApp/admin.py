import code
from django.contrib import admin
from .models import Student, Code


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

class CodesCustomAdmin(admin.ModelAdmin):
    list_display = (
        'code', 
        'type', 
        'duration',
    )
    list_filter = (
        'code', 
        'type', 
        'duration',
    )

admin.site.register(Student, StudentCustomAdmin)
admin.site.register(Code, CodesCustomAdmin)
