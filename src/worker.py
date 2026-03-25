from celery import Celery
from fastapi_mail import NameEmail
from asgiref.sync import async_to_sync
from src.mail import mail, create_message

celery_app = Celery()

celery_app.config_from_object("src.config")


@celery_app.task
def send_email(recipients: list[NameEmail], subject: str, body: str):
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body
    )

    async_to_sync(mail.send_message)(message)
