from django.core.management.base import BaseCommand
from django.conf import settings

from telegram import Bot
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram import Update
from telegram.utils.request import Request

from bot.models import Message, Profile


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e
    return inner


"""Обработчик команды /start
"""


@log_errors
def do_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': username
        }
    )
    update.message.reply_text("Я бот, который будет присылать тебе заявки из ХД, "
                              "если ты обладаешь паролем для авторизации \n"
                              "Для справки пишите /help"
                              )


"""Обработчик команды /help
"""


@log_errors
def do_help(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )
    update.message.reply_text("Список комманд: \n"
                              "/start - начало работы \n"
                              "/login - ввести пароль для регистрации под определенным пользователем \n"
                              "/logout - сбросить текущую авторизацию \n"
                              "/stop - не присылать уведомления \n"
                              )


class Command(BaseCommand):
    help = 'Телеграм-бот для получения новых заявок из ХД'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
            con_pool_size=12,
        )
        bot = Bot(
            request=request,
            token=settings.BOT_TOKEN
        )
        print('Бот запущен!')
        # обработчики
        updater = Updater(
            bot=bot,
            workers=8,

        )

        # Обработчик команды /start
        start_handler = CommandHandler('start', do_start)
        updater.dispatcher.add_handler(start_handler)

        # Обработчик команды /help
        help_handler = CommandHandler('help', do_help)
        updater.dispatcher.add_handler(help_handler)


        # Запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
