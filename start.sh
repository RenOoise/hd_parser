#!/bin/bash

venv/bin/python ./manage.py runserver 0.0.0.0:8000 &
venv/bin/python ./manage.py parser &
venv/bin/python ./manage.py bot