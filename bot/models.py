from django.db import models
from parser.models import TaskExecutor, Task, ExecutorsAndTasksId

'''
Профили пользователей в телеге
'''


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в тг',
        unique=True,
    )
    name = models.TextField(
        verbose_name='Имя пользователя в тг',
    )

    is_registered = models.BooleanField(
        verbose_name='Зарегистрирован',
        default=False,
    )

    def __str__(self):
        return f'#{self.external_id}, {self.name}'

    class Meta:
        verbose_name = 'Профиль тг'
        verbose_name_plural = 'Профили тг'


'''
Принятые ботом сообщения
'''


class Message(models.Model):
    profile = models.ForeignKey(
        to='Profile',
        verbose_name='Профиль тг',
        on_delete=models.PROTECT,
    )
    text = models.TextField(
        verbose_name='Текст сообщения',
    )
    created_at = models.DateTimeField(
        verbose_name='Время получения',
        auto_now=True,
    )

    def __str__(self):
        return f'Сообщение {self.pk} от {self.profile}'

    class Meta:
        verbose_name = 'Полученное сообщение'
        verbose_name_plural = 'Полученные сообщения'


class UserSubscriptions(models.Model):
    profile_id = models.ForeignKey(
        to=Profile,
        verbose_name='Профиль тг',
        on_delete=models.PROTECT,
    )

    executor_id = models.ForeignKey(
        to=TaskExecutor,
        verbose_name='Исполнитель',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f'{self.profile_id} подписан на исполнителя {self.executor_id}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class SentTask(models.Model):
    task_id = models.ForeignKey(
        to=Task,
        verbose_name='Заявка',
        on_delete=models.PROTECT,
    )

    profile_id = models.ForeignKey(
        to='Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    is_sent = models.BooleanField(
        verbose_name='Отправлено в тг',
        default=False,
    )

    def __str__(self):
        return f'Заявка {self.task_id} отправлена пользователю {self.profile_id}: {self.is_sent}'

    class Meta:
        verbose_name = 'Отправленная заявка'
        verbose_name_plural = 'Отправленные заявки'
