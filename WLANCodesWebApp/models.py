from django.db import models


class Code(models.Model):
    TYPE_CHOICES = [
        ('h', 'Stunden'),
        ('d', 'Tage'),
    ]
    code = models.CharField(max_length=10)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    duration = models.IntegerField()


class Student(models.Model):
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=3)
    firstname = models.CharField(max_length=50)
    email = models.CharField(max_length=20)
    date = models.DateField(blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)


class ListDeletion(models.Model):
    deletecode = models.CharField(max_length=10)
