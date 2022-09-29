FROM python:3.8-bullseye

WORKDIR /bot

COPY requirements.txt /bot/
RUN pip install -r requirements.txt

COPY . /bot

CMD python bot.py