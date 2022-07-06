from celery import shared_task
import telegram_send
import time


@shared_task
def send_massive_telegram(messages):
    time.sleep(10)
    telegram_send.send(messages=messages)