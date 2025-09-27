from celery import shared_task
from utils.text_to_speech import generate_audio as generate_audio_func

@shared_task
def generate_audio(card_id):
    """
    Асинхронная задача для генерации аудио
    """
    return generate_audio_func(card_id)

@shared_task
def send_telegram_reminders():
    """
    Задача для отправки напоминаний в Telegram
    """
    from apps.telegram_bot.services import send_daily_reminders
    send_daily_reminders()
