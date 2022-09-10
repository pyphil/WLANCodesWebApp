from django.shortcuts import render, redirect
from .models import Student
from .forms import StudentForm


def codes(request):
    return render(request, 'codes.html', {'text': "12345-67891"})


def new_student(request):
    if request.method == 'GET':
        f = StudentForm()
        return render(request, 'new_student.html', {'form': f})
    if request.method == 'POST':
        f = StudentForm(request.POST)
        if f.is_valid():
            f.save()
        return redirect('codes')


def students(request):
    students = Student.objects.all()
    if request.method == 'GET':
        return render(request, 'students.html', {'students': students})
