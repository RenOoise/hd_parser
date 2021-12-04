from django.db import models

'''
Исполнители заявок
'''


class TaskExecutor(models.Model):
    fullname = models.TextField(
        verbose_name='Полное имя исполнителя',
    )

    def __str__(self):
        return f'{self.fullname}'

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


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

    task_executor = models.TextField(
        verbose_name='Исполнитель заявки',
    )

    task_category = models.TextField(
        verbose_name='Категория заявки',
        default='Не указан'
    )

    task_changed = models.TextField(
        verbose_name='Изменена',
    )

    task_parse_time = models.DateTimeField(
        verbose_name='Время парсинга',
        auto_now=True,
    )

    def __str__(self):
        return f'Заявка {self.external_id} от {self.task_creator_name} для {self.task_executor}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
