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
import logging


logger = logging.getLogger(__name__)
load_dotenv()


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
            print(task)
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
                        print('DEBUG: Исполнитель уже существует в базе')

                    # связываем каждую заявку с исполнителями
                    executors_and_tasks_id = ExecutorsAndTasksId(
                        task_id=Task.objects.get(external_id=task[0]),
                        executor_id=TaskExecutor.objects.get(fullname=executor)
                    )
                    executors_and_tasks_id.save()

            else:
                print("DEBUG: Заявка уже существует в базе")
        else:
            print('DEBUG: found empty list')


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Приложение парсинга страниц ХелпДеска'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            parse,
            trigger=CronTrigger(minute="*/2"),  # Каждые 2 минуты
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
