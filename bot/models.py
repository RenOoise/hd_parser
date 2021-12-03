from django.db import models



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
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
