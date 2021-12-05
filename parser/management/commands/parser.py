import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import Session

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from parser.models import Task, TaskExecutor, ExecutorsAndTasksId
from bot.models import UserSubscriptions, Profile
import logging

from telegram import Bot
from telegram.utils.request import Request

logger = logging.getLogger(__name__)
load_dotenv()
request = Request(
    connect_timeout=0.5,
    read_timeout=1.0,
)
bot = Bot(
    request=request,
    token=settings.BOT_TOKEN
)


def send_task_to_subs(task_id):
    task = Task.objects.get(external_id=int(task_id))
    executors = list()
    for tasks in ExecutorsAndTasksId.objects.filter(task_id=task):
        executors.append(tasks.executor_id)

    profiles = list()
    for executor in executors:
        for profile in UserSubscriptions.objects.filter(executor_id=executor):
            profiles.append(profile.profile_id.id)

    for profile in profiles:
        t_u = Profile.objects.get(id=profile)
        bot.send_message(chat_id=t_u.external_id, text=f"Новая заявка от {task.task_creator_name}:\n {task.task_name}")


def parse():
    s = Session()
    s.post(os.getenv('URL'), {"login": os.getenv('LOGIN'), "password": os.getenv('PASSWORD')})
    page_signed_in = s.get(os.getenv('TASK_URL'))

    soup = BeautifulSoup(page_signed_in.text, features="html.parser")

    main_table = soup.find('table', attrs={'class': 'data resizable-grid'})
    data = list()
    rows = main_table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values

    for task in data:
        if len(task) != 0:
            if not Task.objects.filter(external_id=int(task[0])).exists():
                # добавляем заявку в таблицу заявок
                new_tasks = Task(
                    external_id=int(task[0]),
                    task_name=task[1],
                    # task_status=0 # пока не парсится
                    task_creator_name=task[2],
                    task_changed=task[4],
                )
                new_tasks.save()
                # проходимся итерацией по исполнителям из полученной строки
                for executor in task[3].split(", "):
                    if not TaskExecutor.objects.filter(fullname=executor).exists():
                        # добавляем каждого отдельного исполнителя в таблицу исполнителей
                        add_executor = TaskExecutor(
                            fullname=executor
                        )
                        add_executor.save()
                    else:
                        pass
                    # связываем каждую заявку с исполнителями
                    executors_and_tasks_id = ExecutorsAndTasksId(
                        task_id=Task.objects.get(external_id=task[0]),
                        executor_id=TaskExecutor.objects.get(fullname=executor)
                    )
                    executors_and_tasks_id.save()

                send_task_to_subs(int(task[0]))

            else:
                pass
        else:
            logger.debug("Нашелся пустой список")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Приложение парсинга страниц IntraService'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            parse,
            trigger=CronTrigger(second="*/30"),  # Каждые 2 минуты
            id="parse",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлено задание 'parse'.")

        try:
            logger.info("Запускаю планировщик...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Останавливаю планировщик...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")
