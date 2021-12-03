from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os

from requests import Session

load_dotenv()

URL = os.getenv('URL')
TASK_URL = os.getenv('TASK_URL')
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')

s = Session()
s.post(URL, {"login": LOGIN, "password": PASSWORD})
page_signed_in = s.get(TASK_URL)

soup = BeautifulSoup(page_signed_in.text)

main_table = soup.find('table', attrs={'class': 'data resizable-grid'})
data = list()
rows = main_table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])  # Get rid of empty values
print(data)
