from celery import Celery
from fastapi_mail import NameEmail
from asgiref.sync import async_to_sync
from src.mail import mail, create_message
from src.config import Config

celery_app = Celery(
    "bookly-worker",
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
    broker_connection_retry_on_startup=True
)


@celery_app.task
def send_email(recipients: list[NameEmail], subject: str, body: str):
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body
    )

    async_to_sync(mail.send_message)(message)
