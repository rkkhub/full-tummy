FROM python:3.8-slim-buster
LABEL MAINTAINTER=rkkmailbox@gmail.com

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r ./requirements.txt

RUN useradd --create-home -ms /bin/bash -U dev

USER dev