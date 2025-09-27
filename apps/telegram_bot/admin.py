from django.contrib import admin
from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_username', 'telegram_chat_id', 'daily_reminders_enabled', 'reminder_time')
    list_filter = ('daily_reminders_enabled', 'linked_at')
    search_fields = ('user__username', 'telegram_username')
    readonly_fields = ('linked_at',)