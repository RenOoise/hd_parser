# Generated by Django 3.2.9 on 2021-12-04 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0004_auto_20211204_2253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='task_executor',
        ),
    ]
