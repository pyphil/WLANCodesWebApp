from django.db import models


class Profile(models.Model):
    user_email = models.EmailField()
    uuid = models.CharField(max_length=32)

    def __str__(self):
        return self.user_email