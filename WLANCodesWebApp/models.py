from django.db import models


class Code(models.Model):
    TYPE_CHOICES = [
        ('h', 'Stunde(n)'),
        ('d', 'Tag(e)'),
        ('y', 'Jahr'),
    ]
    code = models.CharField(max_length=11)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    duration = models.IntegerField()


class Student(models.Model):
    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    group = models.CharField(max_length=3)
    email = models.CharField(max_length=30)
    date = models.DateTimeField(blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)


class CodeDeletion(models.Model):
    code_to_delete = models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    group = models.CharField(max_length=3)


class Config(models.Model):
    NAME_CHOICES = [
        ('noreply-mail', 'noreply-E-Mail zum Versand der Schadenmeldung'),
    ]
    name = models.CharField(max_length=50, choices=NAME_CHOICES)
    setting = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.setting
