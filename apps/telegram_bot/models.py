from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    """Связь пользователя Django с Telegram аккаунтом"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram'
    )
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} (TG: {self.telegram_id})"


class BotMessage(models.Model):
    """Логирование сообщений бота"""
    telegram_id = models.BigIntegerField()
    message_text = models.TextField()
    response_text = models.TextField(blank=True)
    command = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.telegram_id}"