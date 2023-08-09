from django.shortcuts import render, redirect
from .models import Student, Code, CodeDeletion, Config
from .forms import StudentForm, MailForm
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from threading import Thread


@login_required
def codes(request):
    # Zugriff nur mit access key in production
    if not request.session.get('has_access'):
        try:
            access = Config.objects.get(name='access')
            ACCESSKEY = access.text
        except Config.DoesNotExist:
            # development
            request.session['has_access'] = True
        else:
            if request.GET.get('access') != ACCESSKEY:
                return render(request, 'NoAccess.html')
            else:
                request.session['has_access'] = True
                return redirect('/')
    elif request.GET.get('access') and request.session.get('has_access'):
        return redirect('/')

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


@staff_member_required
def new_student(request):
    if request.method == 'GET':
        f = StudentForm()
        return render(request, 'new_student.html', {'form': f})
    if request.method == 'POST':
        f = StudentForm(request.POST)
        if f.is_valid():
            f.save()
        return redirect('codes')


@staff_member_required
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


@staff_member_required
def delete_student(request, id=None):
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
        if request.POST.get('delete_all'):
            # Delete all students
            Student.objects.all().delete()
        return redirect('students')

    if id == 'all':
        # render ohne context aber alert "Sicher dass alle gelöscht werden sollen.. Keine Löschliste..."
        return render(request, 'delete_student.html', {'alert_delete_all': True})
    else:
        obj = Student.objects.get(id=id)
        context = {
            'name': obj.name,
            'firstname': obj.firstname,
            'group': obj.group,
            'student_id': obj.id,
        }
        return render(request, 'delete_student.html', context)


@staff_member_required
def students(request, alert=None):
    try:
        mail_text_obj = Config.objects.get(name='mail_text')
    except Config.DoesNotExist:
        mail_text_obj = Config.objects.create(name='mail_text', setting='mail_text')

    # check remaining codes
    remaining_year = len(Code.objects.filter(type='y', duration=1))

    if request.method == 'POST':
        if request.POST.get('checked'):
            # put checked students in a list
            student_ids = request.POST.getlist('checkbox')
            if student_ids == []:
                alert = 0
            else:
                # check number of codes
                if remaining_year >= len(student_ids):
                    alert = 1
                    thread = mail_thread(student_ids)
                    thread.start()
                else:
                    alert = 2

        if request.POST.get('send'):
            # check number of codes
            if remaining_year > 0:
                # put one student in a list
                student_ids = []
                student_ids.append(request.POST.get('send'))
                alert = 1
                thread = mail_thread(student_ids)
                thread.start()
            else:
                alert = 2

        if request.POST.get('send_all'):
            # Send a code to all students in the database
            students = Student.objects.all()
            student_ids = []
            for student in students:
                student_ids.append(student.id)
            # check number of codes
            if remaining_year >= len(student_ids):
                alert = 1
                thread = mail_thread(student_ids)
                thread.start()
            else:
                alert = 2

        if request.POST.get('save_mail_text'):
            mail_form = MailForm(request.POST, instance=mail_text_obj)
            alert = 0
            if mail_form.is_valid():
                mail_form.save()

        if request.GET.get('search'):
            return redirect('/students/' + str(alert) + '?search=' + str(request.GET.get('search')))
        else:
            return redirect('/students/' + str(alert))

    mail_form = MailForm(instance=mail_text_obj)
    if request.GET.get('search') is not None:
        searchterm = str(request.GET.get('search'))
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

    return render(request, 'students.html', {
        'students': students,
        'alert': alert,
        'mail_form': mail_form,
        'remaining_year': remaining_year,
        'search_string': request.GET.get('search'),
        }
    )


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
            mail_text_obj = Config.objects.get(name='mail_text')
            mail_text = mail_text_obj.text
            mail_text = mail_text.replace('#NAME#', student.firstname)
            mail_text = mail_text.replace('#CODE#', student.code)

            send_mail(
                'WLAN-CODE',
                mail_text,
                self.noreply,
                [student.email],
                fail_silently=True,
            )


@staff_member_required
def codedeletion(request):
    if request.method == 'GET':
        try:
            lnk_controller = Config.objects.get(name='lnk_controller')
            lnk_controller = lnk_controller.setting
        except Config.DoesNotExist:
            lnk_controller = "#"
        deletions = CodeDeletion.objects.all()
        return render(request, 'codedeletion.html', {
            'deletions': deletions,
            'lnk_controller': lnk_controller,
            }
        )
    if request.method == 'POST':
        obj = CodeDeletion.objects.get(id=int(request.POST.get('delete')))
        obj.delete()
        return redirect('codedeletion')


@staff_member_required
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
                else:
                    student = Student.objects.filter(email=item[3].strip()).first()
                    student.name = item[0].strip()
                    student.firstname = item[1].strip()
                    student.group = item[2].strip()
                    student.save()

        return redirect('students')
