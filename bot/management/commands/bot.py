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
from bot.models import Profile, Message, UserSubscriptions
from parser.models import TaskExecutor, Task, ExecutorsAndTasksId

request = Request(
    connect_timeout=0.5,
    read_timeout=1.0,
)
bot = Bot(
    request=request,
    token=settings.BOT_TOKEN
)


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


'''
Генератор кнопок исполнителей
'''


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


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
        if Profile.objects.get(external_id=chat_id).is_registered:
            update.message.reply_text(f"Привет, {username}! Я бот, который будет присылать тебе заявки из ХД "
                                      "по мере их поступления.\n"
                                      "Сбор заявок с веб-интерфейса выполняется каждые 5 минут, так что могут "
                                      "быть небольшие задержки\n"
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
        if Profile.objects.get(external_id=chat_id).is_registered:
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
    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get(external_id=chat_id).is_registered:
            update.message.reply_text("Список команд: \n"
                                      "/start - начало работы \n"
                                      "/login - ввести пароль для доступа к боту\n"
                                      "/logout - сбросить текущую авторизацию \n"
                                      "/subscribe - подписаться на исполнителей\n"
                                      "/unsubscribe - отписаться от исполнителей\n"
                                      "/stop - не присылать уведомления \n"
                                      )


@log_errors
def do_register(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )
    m = Message(
        profile=p,
        text=text,
    )

    m.save()

    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username

    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get(external_id=chat_id).is_registered:
            update.message.reply_text('Команда не распознана.\n'
                                      'Если хочешь пообщаться, то это не ко мне.')
        else:
            if update.message.text == settings.SUBSCRIPTION_KEY:
                profile_register = Profile.objects.get(external_id=chat_id)
                profile_register.is_registered = True
                profile_register.save()
                update.message.reply_text('Странно, ты откуда-то знаешь пароль.\n'
                                          'Добро пожаловать!\n'
                                          'Теперь можешь подписаться на нужные тебе заявки.\n'
                                          'Просто напиши /subscribe и выбери исполнителя.')


@log_errors
def do_subscribe(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if update.message.from_user.username is None:
        username = 'NoName'
    else:
        username = update.message.from_user.username

    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get(external_id=chat_id).is_registered:
            list_of_executors = list()
            button_list = []
            for each in TaskExecutor.objects.all():
                button_list.append(InlineKeyboardButton(each.fullname, callback_data=f'subscribe:{each.id}'))
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=1))
            update.message.reply_text(
                text="В БД есть несколько исполнителей.\nВыбери на кого нужно тебя подписать:",
                reply_markup=reply_markup)


@log_errors
def do_unsubscribe(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if Profile.objects.filter(external_id=chat_id).exists():
        if Profile.objects.get(external_id=chat_id).is_registered:
            button_list = list()
            for each in UserSubscriptions.objects.filter(profile_id=Profile.objects.get(external_id=chat_id)):
                print(each)
                executor_profile = TaskExecutor.objects.get(fullname=each.executor_id)
                button_list.append(InlineKeyboardButton(
                    executor_profile.fullname,
                    callback_data=f'unsubscribe:{executor_profile.id}'),
                )
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=1))
            update.message.reply_text(
                text="Выбери от кого тебя отписать:",
                reply_markup=reply_markup,
            )


'''
Обработчик событий с клавиатур
'''


@log_errors
def keyboard_callback_handler(update: Update, chat_data=None, **kwargs):
    query = update.callback_query
    data = query.data.split(":")
    chat_id = update.effective_message.chat_id
    p = Profile.objects.get(external_id=chat_id)
    if data[0] == 'subscribe':
        selected_executor = TaskExecutor.objects.get(id=int(data[1]))

        subscribed_to = UserSubscriptions.objects.filter(profile_id=p, executor_id=selected_executor).exists()
        if subscribed_to:
            update.effective_message.edit_text(text=f"Ты уже подписан на исполнителя {selected_executor.fullname}")
        else:
            subscribe_to = UserSubscriptions(
                profile_id=p,
                executor_id=selected_executor,
            )
            subscribe_to.save()
            update.effective_message.edit_text(text=f"Подписал тебя на заявки для {selected_executor.fullname}")
    elif data[0] == 'unsubscribe':
        selected_executor = TaskExecutor.objects.get(id=int(data[1]))

        subscribed_to = UserSubscriptions.objects.filter(profile_id=p, executor_id=selected_executor).delete()
        if subscribed_to:
            update.effective_message.edit_text(text=f"Отписал тебя от {selected_executor.fullname}")
        else:

            update.effective_message.edit_text(text=f"Ты не подписан на {selected_executor.fullname}, "
                                                    f"это какая-то ошибка.")


class Command(BaseCommand):
    help = 'Телеграм-бот для получения новых заявок из ХД'

    def handle(self, *args, **options):
        request_ = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
            con_pool_size=12,
        )
        bot_ = Bot(
            request=request_,
            token=settings.BOT_TOKEN
        )
        print('Бот запущен!')
        # обработчики
        updater = Updater(
            bot=bot_,
            workers=8,

        )

        # Обработчик команды /start
        start_handler = CommandHandler('start', do_start)
        updater.dispatcher.add_handler(start_handler)

        # Обработчик команды /help
        help_handler = CommandHandler('help', do_help)
        updater.dispatcher.add_handler(help_handler)

        # обработчик команды /login
        login_handler = CommandHandler('login', do_login)
        updater.dispatcher.add_handler(login_handler)

        # обработчик команды /subscribe
        subscribe_handler = CommandHandler('subscribe', do_subscribe)
        updater.dispatcher.add_handler(subscribe_handler)


        # обработчик команды /unsubscribe
        unsubscribe_handler = CommandHandler('unsubscribe', do_unsubscribe)
        updater.dispatcher.add_handler(unsubscribe_handler)


        # Обработчик всех сообщений
        message_handler = MessageHandler(Filters.text, do_register)
        updater.dispatcher.add_handler(message_handler)

        # Обработчик клавиатур
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True)
        updater.dispatcher.add_handler(buttons_handler)

        # Запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
