from celery import shared_task
from django.core.mail import send_mail
from time import sleep


@shared_task
def send_notification_email(subject, message, recipient_list):
    send_mail(subject, message, 'from@example.com', recipient_list)
    return "Email sent"


@shared_task
def long_computation(x, y):
    sleep(10)
    return x + y