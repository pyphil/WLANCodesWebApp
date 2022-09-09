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
    firstname = models.CharField(max_length=50)
    group = models.CharField(max_length=3)
    code = models.CharField(max_length=10)


class ListDeletion(models.Model):
    deletecode = models.CharField(max_length=10)
