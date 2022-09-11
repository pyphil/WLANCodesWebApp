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


def edit_student(request, id):
    obj = Student.objects.get(id=id)
    if request.method == 'GET':
        f = StudentForm(instance=obj)
        return render(request, 'new_student.html', {'form': f})
    if request.method == 'POST':
        f = StudentForm(request.POST, instance=obj)
        if f.is_valid():
            f.save()
        return redirect('codes')


def delete_student(request, id=None):
    obj = Student.objects.get(id=id)
    if request.method == 'GET':
        context = {
            'name': obj.name,
            'firstname': obj.firstname,
            'group': obj.group,
            'student_id': obj.id,
        }
        return render(request, 'delete_student.html', context)
    if request.method == 'POST':
        if request.POST.get('delete'):
            del_obj = Student.objects.get(id=int(request.POST.get('delete')))
            del_obj.delete()
        return redirect('students')


def students(request):
    students = Student.objects.all()
    if request.method == 'GET':
        return render(request, 'students.html', {'students': students})


def student_import(request):
    if request.method == 'GET':
        return render(request, 'student_import.html', {})
    if request.method == 'POST':
        text = request.POST.get('input')
        for line in text.split('\n'):
            item = line.split(';')
            if Student.objects.filter(email=item[3]):
                pass
            else:
                # import
                Student.objects.create(
                    name=item[0],
                    firstname=item[1],
                    group=item[2],
                    email=item[3],
                )
        return redirect('students')
