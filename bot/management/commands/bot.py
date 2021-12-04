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
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import Handler
from bot.models import Profile


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e
    return inner


"""
Обработчик команды /start
"""


@log_errors
def do_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username

    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get().is_registered:
            update.message.reply_text(f"Привет, {username}! Я бот, который будет присылать тебе заявки из ХД "
                                      "по мере их поступления.\n"
                                      "Сбор заявок с веб-интерфейса выполняется каждые 5 минут, так что могут "
                                      "быть небольшие задержки"
                                      "Для списка команд  пиши /help"
                                      )
        else:
            update.message.reply_text(f'Повторяю еще раз: тебе, {username}, нужен пароль для входа.\n'
                                      'Если он у тебя есть, то пиши /login')
    else:
        p, _ = Profile.objects.get_or_create(
            external_id=chat_id,
            defaults={
                'name': username
            }
        )
        update.message.reply_text(f'Привет, {username}!\n'
                                  'Для получения доступа к этому боту нужно обладать паролем для регистрации.\n'
                                  'Если он у тебя есть используй команду /login для входа.'
                                  )


'''
Обработчик команды /login
'''


@log_errors
def do_login(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username

    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get().is_registered:
            update.message.reply_text(f"{username}! Ты уже зарегистрирован. Если хочешь подписаться на уведомления "
                                      "для какого-то определенного исполнителя, воспользуйся командой /subscribe\n"
                                      "Для списка команд  пиши /help"
                                      )
        else:
            update.message.reply_text('Вводи свой пароль после этого сообщения')
    else:
        p, _ = Profile.objects.get_or_create(
            external_id=chat_id,
            defaults={
                'name': username
            }
        )
        update.message.reply_text('Вводи свой пароль после этого сообщения')


"""
Обработчик команды /help
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


@log_errors
def do_register(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username

    if Profile.objects.filter(external_id=chat_id).exists():
        print('В базе есть')
        if Profile.objects.get().is_registered:
            print('Зареган')
            update.message.reply_text('Команда не распознана.\n'
                                      'Если хочешь пообщаться, то это не ко мне.')
        else:
            print(update.message.text)
            print(settings.SUBSCRIPTION_KEY)
            if update.message.text == settings.SUBSCRIPTION_KEY:
                profile_register = Profile.objects.get(external_id=chat_id)
                profile_register.is_registered = True
                profile_register.save()
                update.message.reply_text('Странно, ты откуда-то знаешь пароль.\n'
                                          'Добро пожаловать!\n'
                                          'Теперь можешь подписаться на нужные тебе заявки.\n'
                                          'Просто напиши /subscribe и выбери исполнителя.')


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

        login_handler = CommandHandler('login', do_login)
        updater.dispatcher.add_handler(login_handler)

        # Обработчик всех сообщений
        message_handler = MessageHandler(Filters.text, do_register)
        updater.dispatcher.add_handler(message_handler)

        # Запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
