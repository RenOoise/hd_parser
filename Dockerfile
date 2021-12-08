FROM python:3.10-alpine as builder

WORKDIR /usr/src/hd_parser

ENV PYTHONDONRWITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev


RUN pip install --upgrade pip
RUN pip install flake8
COPY . .

RUN flake8 --ignore=E501,F401 .

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/hd_parser/wheels -r requirements.txt

FROM python:3.10-alpine

RUN mkdir -p /home/hd_parser

RUN addgroup -S hd_parser && adduser -S hd_parser -G hd_parser

ENV HOME=/home/hd_parser
ENV APP_HOME=/home/hd_parser/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

RUN apk update && apk add libpq
COPY --from=builder /usr/src/hd_parser/wheels /wheels
COPY --from=builder /usr/src/hd_parser/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

COPY . $APP_HOME

RUN chown -R hd_parser:hd_parser $APP_HOME

USER hd_parser

ENTRYPOINT ["/home/hd_parser/app/entrypoint.sh"]