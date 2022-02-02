### **Парсер хелпдеска в телеграм бот на основе джанго**

**Для запуска в Docker:**  
```docker-compose -f docker-compose.yml up -d --build```

**Файл .env должен содержать следующие переменные:**  
```
SUBSCRIPTION_KEY=секретный ключ для доступа к боту  
URL=http://адрес хелпдеска/  
LOGIN=hd_parser # пользователь хеплдеска  
PASSWORD=hd_parser # пароль хелпдеска  
TASK_URL=http://192.168.1.1/Task # сылка на первую страницу с заявками  
SECRET_KEY=mysecret # секрет кей джанго  
BOT_TOKEN=22222222:null # токен бота ТГ  
SUBSCRIPTION_KEY=секретный ключ для доступа к боту  
DEBUG=0 # дебаг on/off  
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1] * # разрешенные хосты для джанго
```

**Файл .env.db должен содержать следующие переменные:**  
```
SQL_ENGINE=django.db.backends.postgresql # тип БД  
DB_NAME=hd_parser # имя БД  
DB_USER=hd_parser # юзер БД  
DB_PASSWORD=hd_parser # пароль юзера БД  
DB_HOST=db # IP-хоста или хостнейм  
DB_PORT=5432 # порт DB
```
