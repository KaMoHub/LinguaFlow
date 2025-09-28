# apps/telegram_bot/admin.py
from django.contrib import admin
from .models import TelegramUser, BotMessage # Убедитесь, что импортировали обе модели

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    # Используем только существующие поля из модели TelegramUser
    list_display = ('user', 'telegram_id', 'username', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active', 'created_at') # Фильтруем по существующим полям
    search_fields = ('user__username', 'username', 'first_name', 'last_name', 'telegram_id') # Поля для поиска
    readonly_fields = ('created_at', 'updated_at') # Поля только для чтения (если хотите)
    # Дополнительно: настройка отображения полей при редактировании
    # fields = ('user', 'telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'created_at', 'updated_at')

@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    # Пример настройки админки для BotMessage
    list_display = ('telegram_id', 'command', 'created_at')
    list_filter = ('created_at', 'command')
    search_fields = ('telegram_id', 'message_text', 'response_text')
    readonly_fields = ('created_at',)

# admin.py