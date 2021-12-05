FROM python:3.10
WORKDIR /hd_parser
RUN python -m venv venv
COPY requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt
COPY . .
RUN venv/bin/python manage.py makemigrations
RUN venv/bin/python manage.py migrate
EXPOSE 8000
RUN chmod a+x start.sh
ENTRYPOINT ["./start.sh"]