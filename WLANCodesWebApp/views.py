from tokenize import group
from django.shortcuts import render, redirect
from .models import Student, Code, CodeDeletion, Config
from .forms import StudentForm
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required


def codes(request):
    return render(request, 'codes.html', {'text': "12345-67891"})


@login_required
def new_student(request):
    if request.method == 'GET':
        f = StudentForm()
        return render(request, 'new_student.html', {'form': f})
    if request.method == 'POST':
        f = StudentForm(request.POST)
        if f.is_valid():
            f.save()
        return redirect('codes')


@login_required
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


@login_required
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


@login_required
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
        # put oldcode on delete list
        if oldcode != None:
            CodeDeletion.objects.create(
                code_to_delete=oldcode,
                name=student.name,
                firstname=student.firstname,
                group=student.group
            )
        newcode = Code.objects.filter(type='y').first()
        student.code = newcode.code
        # delete used code
        newcode.delete()
        student.date = datetime.today()
        student.save()
        mail_text = (
            "Hallo " + student.firstname + ",\n\n" +
            "hiemit erhältst du deinen WLAN-Code für das aktuelle Schuljahr. " + 
            "Der Code kann nur einmalig auf einem Gerät aktiviert werden, d.h. " +
            "falls du ein Tablet hast, dein Tablet, ansonsten dein Smartphone.\n\n" +
            "Dein Code lautet: \n\n" +
            student.code + "\n\n" +
            "Hinweis: Eine Weitergabe des Codes ist nicht möglich. Falls du einen " +
            "neuen Code brauchst, wird der alte Code deaktiviert."
        )
        noreply = Config.objects.get(name="noreply-mail")
        send_mail(
            'WLAN-CODE',
            mail_text,
            noreply,
            [student.email],
            fail_silently=True,
        )
        return redirect('students')


@login_required
def codedeletion(request):
    if request.method == 'GET':
        deletions = CodeDeletion.objects.all()
        return render(request, 'codedeletion.html', {'deletions': deletions})
    if request.method == 'POST':
        obj = CodeDeletion.objects.get(id=int(request.POST.get('delete')))
        obj.delete()
        return redirect('codedeletion')


@login_required
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
