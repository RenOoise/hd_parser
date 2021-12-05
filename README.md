# hd_parser
Парсер хелпдеска в телеграм бот на основе джанго

Для запуска в Docker:

docker run -it -d -p 8000:8000 -v ~/hd_parser/db.sqlite3:/hd_parser/db.sqlite3  hd_parser:latest --restart always
