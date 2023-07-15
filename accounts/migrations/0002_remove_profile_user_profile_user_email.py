# Generated by Django 4.1.5 on 2023-07-15 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.AddField(
            model_name='profile',
            name='user_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
    ]
