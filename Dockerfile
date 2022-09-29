FROM python:3.8-bullseye

WORKDIR /bot

COPY requirements.txt /bot/
RUN apt-get update && apt-get install ffmpeg -y
RUN pip install -r requirements.txt

COPY . /bot

CMD python bot_run.py