# hd_parser

Парсер хелпдеска в телеграм бот на основе джанго

Для запуска в Docker:

docker run -it -d -p 8000:8000 -v ~/hd_parser/db.sqlite3:/hd_parser/db.sqlite3 hd_parser:latest --restart always

Файл .env должен содержать следующие переменные:

URL=http://адрес хелпдеска/

LOGIN=пользователь хеплдеска

PASSWORD=пароль хелпдеска

TASK_URL=http://"адрес_хелпдеска"/Task

SECRET_KEY=секрет кей джанго

BOT_TOKEN=токен бота ТГ

SUBSCRIPTION_KEY=секретный ключ для доступа к боту

