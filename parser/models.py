from django.db import models

'''
Исполнители заявок
'''


class TaskExecutor(models.Model):
    fullname = models.TextField(
        verbose_name='Полное имя исполнителя',
    )


'''
Заявки
'''


class Task(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID заявки',
        unique=True,
    )
    task_name = models.TextField(
        verbose_name='Название заявки'
    )
    task_status = models.TextField(
        verbose_name='Статус заявки'
    )
    task_creator_name = models.TextField(
        verbose_name='Заявитель'
    )
    task_executor = models.ForeignKey(
        to='TaskExecutor',
        verbose_name='Исполнитель заявки',
        on_delete=models.PROTECT,
    )
    task_changed = models.TextField(
        verbose_name='Изменена'
    )
