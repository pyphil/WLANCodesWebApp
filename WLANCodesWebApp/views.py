from django.shortcuts import render, redirect
from .models import Student, Code, CodeDeletion, Config
from .forms import StudentForm
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from threading import Thread


@login_required
def codes(request):
    remaining_1 = len(Code.objects.filter(type='h', duration=1))
    remaining_2 = len(Code.objects.filter(type='h', duration=2))
    remaining_3 = len(Code.objects.filter(type='d', duration=1))

    try:
        code = request.session['code']
        active = request.session['active']
        del request.session['code']
        del request.session['active']
    except KeyError:
        code = 0
        active = 0
    if request.GET.get('c'):
        request.session['active'] = request.GET.get('c')
        if request.GET.get('c') == "1":
            obj = Code.objects.filter(type='h', duration=1).first()
            if obj is None:
                code = "- leer -"
            else:
                code = obj.code
                obj.delete()
        if request.GET.get('c') == "2":
            obj = Code.objects.filter(type='h', duration=2).first()
            if obj is None:
                code = "- leer -"
            else:
                code = obj.code
                obj.delete()
        if request.GET.get('c') == "3":
            obj = Code.objects.filter(type='d', duration=1).first()
            if obj is None:
                code = "- leer -"
            else:
                code = obj.code
                obj.delete()
        request.session['code'] = code
        return redirect('codes')
    else:
        context = {
            'code': code,
            'active': active,
            'remaining_1': remaining_1,
            'remaining_2': remaining_2,
            'remaining_3': remaining_3,
        }
        return render(request, 'codes.html', context)


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
            oldcode = del_obj.code
            # put oldcode on delete list
            if oldcode is not None:
                CodeDeletion.objects.create(
                    code_to_delete=oldcode,
                    name=del_obj.name,
                    firstname=del_obj.firstname,
                    group=del_obj.group
                )
            del_obj.delete()
        return redirect('students')


@login_required
def students(request, alert=None):
    if request.method == 'GET':
        if request.GET.get('search') is not None:
            searchterm = str(request.GET.get('search'))
            print(searchterm)
            students = (
                Student.objects.filter(name__icontains=searchterm) |
                Student.objects.filter(firstname__icontains=searchterm) |
                Student.objects.filter(code__icontains=searchterm)
            )
        elif request.GET.get('sort') == 'date':
            students = Student.objects.all().order_by('-date')
        elif request.GET.get('sort') == 'code':
            students = Student.objects.all().order_by('code')
        else:
            students = Student.objects.all().order_by('group', 'name')
        return render(request, 'students.html', {'students': students, 'alert': alert})
    if request.method == 'POST':
        if request.POST.get('checked'):
            # put checked students in a list
            student_ids = request.POST.getlist('checkbox')
            if student_ids == []:
                alert = 0
        elif request.POST.get('send'):
            # put one student in a list
            student_ids = []
            student_ids.append(request.POST.get('send'))
            alert = 1

        thread = mail_thread(student_ids)
        thread.start()

        return redirect('students', alert=alert)


class mail_thread(Thread):
    def __init__(self, student_ids):
        super(mail_thread, self).__init__()
        self.student_ids = student_ids
        self.noreply = Config.objects.get(name="noreply-mail")

    # run method is automatically executed on thread.start()
    def run(self):
        for id in self.student_ids:
            student = Student.objects.get(id=id)
            oldcode = student.code
            # put oldcode on delete list if exists
            if oldcode is not None:
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
                "hiermit erhältst du deinen WLAN-Code für das aktuelle Schuljahr. " +
                "Der Code kann nur einmalig auf einem Gerät aktiviert werden, d.h. " +
                "falls du ein Tablet hast, dein Tablet, ansonsten dein Smartphone.\n\n" +
                "Dein Code lautet: \n\n" +
                student.code + "\n\n" +
                "Hinweis: Eine Weitergabe des Codes ist nicht möglich. Falls du einen " +
                "neuen Code brauchst, wird der alte Code deaktiviert. Bei Problemen wendest " +
                "du dich an die Administratoren (LOB/SCL)"
            )
            send_mail(
                    'WLAN-CODE',
                    mail_text,
                    self.noreply,
                    [student.email],
                    fail_silently=True,
                )


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
            try:
                Student.objects.filter(email=item[3].strip())
            except IndexError:
                pass
            else:
                if not Student.objects.filter(email=item[3].strip()):
                    # import
                    Student.objects.create(
                        name=item[0].strip(),
                        firstname=item[1].strip(),
                        group=item[2].strip(),
                        email=item[3].strip(),
                    )
        return redirect('students')
