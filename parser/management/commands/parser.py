from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from requests import Session

from parser.models import Task, TaskExecutor

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
        empty = []
        if len(task) != 0:
            if Task.objects.filter(external_id=int(task[0])).exists():
                print(task[0])
            else:
                print(task[0], task[1])


class Command(BaseCommand):
    help = 'Приложение парсинга страниц ХелпДеска'

    def handle(self, *args, **options):
            parse()

