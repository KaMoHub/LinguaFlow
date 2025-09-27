from django.core.management.base import BaseCommand
from django.conf import settings
from telegram_bot.services import TelegramBot


class Command(BaseCommand):
    help = 'Set Telegram webhook'

    def handle(self, *args, **options):
        bot = TelegramBot()
        result = bot.set_webhook(settings.TELEGRAM_WEBHOOK_URL)

        if result and result.get('ok'):
            self.stdout.write(
                self.style.SUCCESS('Webhook set successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to set webhook')
            )