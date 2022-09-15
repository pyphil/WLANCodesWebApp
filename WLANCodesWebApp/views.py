from tokenize import group
from django.shortcuts import render, redirect
from .models import Student, Code, CodeDeletion
from .forms import StudentForm
from datetime import datetime


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
        return redirect('students')


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
    if request.method == 'GET':
        if request.GET.get('sort') == 'date':
            students = Student.objects.all().order_by('-date')
            return render(request, 'students.html', {'students': students})
        elif request.GET.get('sort') == 'code':
            students = Student.objects.all().order_by('code')
            return render(request, 'students.html', {'students': students})
        else:
            students = Student.objects.all().order_by('group', 'name')
            return render(request, 'students.html', {'students': students})
    if request.method == 'POST':
        id = int(request.POST.get('send'))
        student = Student.objects.get(id=id)
        oldcode = student.code
        # TODO: put oldcode on delete list
        if oldcode != None:
            CodeDeletion.objects.create(
                code_to_delete=oldcode,
                name=student.name,
                firstname=student.firstname,
                group=student.group
            )
        newcode = Code.objects.filter(type='h').first()
        student.code = newcode.code
        # delete used code
        newcode.delete()
        student.date = datetime.today()
        student.save()
        # TODO: Send Mail
        return redirect('students')


def codedeletion(request):
    if request.method == 'GET':
        deletions = CodeDeletion.objects.all()
        return render(request, 'codedeletion.html', {'deletions': deletions})
    if request.method == 'POST':
        obj = CodeDeletion.objects.get(id=int(request.POST.get('delete')))
        obj.delete()
        return redirect('codedeletion')


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
