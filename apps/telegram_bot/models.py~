from django.db import models
from apps.core.models import TimeStampedModel


class TelegramUser(TimeStampedModel):
    """Связь пользователя с Telegram аккаунтом"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='telegram')
    telegram_chat_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    daily_reminders_enabled = models.BooleanField(default=True)
    reminder_time = models.TimeField(default='20:00')  # Время напоминания по умолчанию
    linked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.telegram_username}" if self.telegram_username else f"ID: {self.telegram_chat_id}"

