from django.shortcuts import render, redirect
from .forms import StudentForm


def codes(request):
    return render(request, 'codes.html', {'text': "12345-67891"})


def students(request):
    if request.method == 'GET':
        f = StudentForm()
        return render(request, 'students.html', {'form': f})
    if request.method == 'POST':
        f = StudentForm(request.POST)
        if f.is_valid():
            f.save()
        return redirect('codes')
