from django.forms import ModelForm
from django import forms
from .models import Student, Config


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = (
            'name',
            'firstname',
            'group',
            'email',
            'date',
            'code',
        )


class MailForm(ModelForm):
    class Meta:
        model = Config
        fields = (
            'text',
        )
        labels = {
            'text': 'E-Mail-Text für den Codeversand',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
