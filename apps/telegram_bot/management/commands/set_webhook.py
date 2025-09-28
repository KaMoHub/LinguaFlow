from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sets the Telegram bot webhook using the configured token and server URL.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='The full URL for the webhook (e.g., https://yourdomain.com/telegram/webhook/). '
                 'If not provided, it will be constructed using SITE_URL from settings and the default path.',
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove the webhook instead of setting it.',
        )

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            self.stderr.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not found in settings.')
            )
            return

        base_url = f"https://api.telegram.org/bot{token}"

        if options['remove']:
            url = f"{base_url}/deleteWebhook"
            response = requests.get(url)
            if response.status_code == 200 and response.json().get('ok'):
                self.stdout.write(
                    self.style.SUCCESS('Webhook successfully removed.')
                )
            else:
                self.stderr.write(
                    self.style.ERROR(f'Failed to remove webhook: {response.text}')
                )
            return

        # Определяем URL для вебхука
        webhook_url = options['url']
        if not webhook_url:
            # Пытаемся получить SITE_URL из настроек, если есть
            # В простом случае разработки можно использовать localhost, но для вебхука нужен публичный URL
            site_url = getattr(settings, 'SITE_URL', None)
            if not site_url:
                # ПРЕДУПРЕЖДЕНИЕ: localhost НЕ ПОДХОДИТ для вебхука, так как Telegram не может добраться до него
                # Этот вариант подходит только для ознакомления или если вы используете сервисы вроде ngrok
                site_url = input("Enter your public site URL (e.g., https://yourdomain.com or ngrok URL): ").strip()
                if not site_url:
                    self.stderr.write(
                        self.style.ERROR('No public site URL provided. Cannot set webhook.')
                    )
                    return
            webhook_url = f"{site_url.rstrip('/')}/telegram/webhook/" # Используем путь из urls.py

        set_url = f"{base_url}/setWebhook"
        payload = {'url': webhook_url}

        # В реальных проектах возможно потребуется указать сертификат или использовать другие параметры
        response = requests.post(set_url, json=payload)

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS(f'Webhook successfully set to: {webhook_url}')
                )
                logger.info(f'Telegram webhook set to: {webhook_url}')
            else:
                self.stderr.write(
                    self.style.ERROR(f'Failed to set webhook: {result.get("description", "Unknown error")}')
                )
                logger.error(f'Failed to set Telegram webhook: {result.get("description", "Unknown error")}')
        else:
            self.stderr.write(
                self.style.ERROR(f'Failed to communicate with Telegram API: {response.status_code} - {response.text}')
            )
            logger.error(f'Failed to set Telegram webhook (API error): {response.status_code} - {response.text}')
