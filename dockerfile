FROM python:3.8-slim-buster
LABEL MAINTAINTER=rkkmailbox@gmail.com

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r ./requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN useradd --create-home -ms /bin/bash -U dev
USER dev