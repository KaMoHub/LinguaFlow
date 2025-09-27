import requests
import logging
from django.conf import settings
from django.urls import reverse
from .models import TelegramUser, BotMessage

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text, parse_mode='HTML', reply_markup=None):
        """Отправка сообщения в Telegram"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

        if reply_markup:
            payload['reply_markup'] = reply_markup

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return None

    def set_webhook(self, url):
        """Установка webhook"""
        webhook_url = f"{url}/telegram/webhook/"
        api_url = f"{self.base_url}/setWebhook?url={webhook_url}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            logger.info(f"Webhook set to: {webhook_url}")
            return response.json()
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return None

    def get_me(self):
        """Получение информации о боте"""
        url = f"{self.base_url}/getMe"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None


class MessageHandler:
    """Обработчик сообщений бота"""

    def __init__(self):
        self.bot = TelegramBot()

    def handle_start(self, chat_id, user_data):
        """Обработка команды /start"""
        welcome_text = """
🤖 <b>LinguaFlow Bot</b>

Добро пожаловать в бот для изучения языков! 

<b>Доступные команды:</b>
/start - Начало работы
/help - Помощь и инструкции  
/stats - Статистика изучения
/connect - Привязать аккаунт
/unlink - Отвязать аккаунт

📚 <b>Что умеет бот:</b>
• Напоминать о повторении слов
• Показывать статистику прогресса
• Отправлять слова для быстрого повторения

Для начала привяжите ваш аккаунт командой /connect
        """

        # Создаем клавиатуру с основными командами
        keyboard = {
            'keyboard': [
                [{'text': '📊 Статистика'}, {'text': '🔄 Повторить'}],
                [{'text': '🔗 Привязать аккаунт'}, {'text': '❓ Помощь'}]
            ],
            'resize_keyboard': True
        }

        self.bot.send_message(chat_id, welcome_text, reply_markup=keyboard)

        # Логируем сообщение
        BotMessage.objects.create(
            telegram_id=chat_id,
            message_text="/start",
            response_text=welcome_text,
            command="start"
        )

    def handle_help(self, chat_id, user_data):
        """Обработка команды /help"""
        help_text = """
📚 <b>LinguaFlow - Помощь</b>

<b>Основные команды:</b>

/start - Начало работы с ботом
/help - Эта справка
/stats - Ваша статистика изучения
/connect - Привязать аккаунт сайта
/unlink - Отвязать аккаунт

<b>Как использовать:</b>
1. Сначала привяжите аккаунт командой /connect
2. Бот будет напоминать о повторении слов
3. Используйте кнопки для быстрого доступа к функциям

<b>Для поддержки:</b>
Если у вас есть вопросы или предложения, свяжитесь с администрацией через сайт.
        """

        self.bot.send_message(chat_id, help_text)

        BotMessage.objects.create(
            telegram_id=chat_id,
            message_text="/help",
            response_text=help_text,
            command="help"
        )

    def handle_connect(self, chat_id, user_data):
        """Обработка команды /connect"""
        # Генерируем уникальный код для привязки
        import secrets
        connection_code = secrets.token_hex(8)

        connect_text = f"""
🔗 <b>Привязка аккаунта</b>

Для привязки вашего аккаунта LinguaFlow:

1. Перейдите на сайт: <b>ваш-сайт.com/telegram/connect/</b>
2. Введите код: <code>{connection_code}</code>
3. Подтвердите привязку

Код действителен 10 минут.

После привязки вы сможете:
• Получать уведомления о повторении
• Просматривать статистику
• Быстро повторять слова через бота
        """

        # Сохраняем код в сессии или временном хранилище
        # Здесь упрощенная версия - в реальности нужно хранить код с привязкой к времени

        self.bot.send_message(chat_id, connect_text)

        BotMessage.objects.create(
            telegram_id=chat_id,
            message_text="/connect",
            response_text=connect_text,
            command="connect"
        )
        return connection_code

    def handle_stats(self, chat_id, user_data):
        """Обработка команды /stats"""
        # Проверяем, привязан ли аккаунт
        try:
            tg_user = TelegramUser.objects.get(telegram_id=chat_id)
            user = tg_user.user

            # Получаем статистику пользователя
            from apps.decks.models import UserWordProgress, Card

            total_cards = Card.objects.filter(deck__user=user).count()
            studied = UserWordProgress.objects.filter(user=user).count()
            mastered = UserWordProgress.objects.filter(user=user, status='mastered').count()

            stats_text = f"""
📊 <b>Ваша статистика</b>

👤 Пользователь: <b>{user.username}</b>
📚 Всего карточек: <b>{total_cards}</b>
📖 Изучается: <b>{studied}</b>
🎯 Выучено: <b>{mastered}</b>

Продолжайте в том же духе! 💪
            """

        except TelegramUser.DoesNotExist:
            stats_text = """
📊 <b>Статистика</b>

Для просмотра статистики необходимо привязать аккаунт.

Используйте команду /connect для привязки вашего аккаунта LinguaFlow.
            """

        self.bot.send_message(chat_id, stats_text)

        BotMessage.objects.create(
            telegram_id=chat_id,
            message_text="/stats",
            response_text=stats_text,
            command="stats"
        )

    def handle_message(self, message_data):
        """Основной обработчик сообщений"""
        chat_id = message_data['chat']['id']
        text = message_data.get('text', '').strip()

        # Логируем входящее сообщение
        BotMessage.objects.create(
            telegram_id=chat_id,
            message_text=text,
            command="message"
        )

        # Обработка команд
        if text.startswith('/'):
            command = text.split('@')[0].lower()  # Убираем username бота если есть

            if command == '/start':
                self.handle_start(chat_id, message_data.get('from', {}))
            elif command == '/help':
                self.handle_help(chat_id, message_data.get('from', {}))
            elif command == '/connect':
                self.handle_connect(chat_id, message_data.get('from', {}))
            elif command == '/stats':
                self.handle_stats(chat_id, message_data.get('from', {}))
            elif command == '/unlink':
                self.handle_unlink(chat_id, message_data.get('from', {}))
            else:
                self.bot.send_message(chat_id, "Неизвестная команда. Используйте /help для списка команд.")
        else:
            # Обработка текстовых сообщений (кнопки)
            if text == '📊 Статистика':
                self.handle_stats(chat_id, message_data.get('from', {}))
            elif text == '❓ Помощь':
                self.handle_help(chat_id, message_data.get('from', {}))
            elif text == '🔗 Привязать аккаунт':
                self.handle_connect(chat_id, message_data.get('from', {}))
            elif text == '🔄 Повторить':
                self.handle_review(chat_id, message_data.get('from', {}))
            else:
                self.bot.send_message(chat_id, "Используйте команды из меню или наберите /help для справки.")

    def handle_unlink(self, chat_id, user_data):
        """Отвязка аккаунта"""
        try:
            tg_user = TelegramUser.objects.get(telegram_id=chat_id)
            tg_user.delete()
            text = "✅ Аккаунт успешно отвязан."
        except TelegramUser.DoesNotExist:
            text = "❌ Аккаунт не был привязан."

        self.bot.send_message(chat_id, text)

    def handle_review(self, chat_id, user_data):
        """Быстрое повторение через бота"""
        try:
            tg_user = TelegramUser.objects.get(telegram_id=chat_id)
            user = tg_user.user

            # Получаем карточку для повторения
            from apps.decks.services import get_cards_for_study_session
            cards = get_cards_for_study_session(user, 'review', limit=1)

            if cards:
                card = cards[0]
                # ИСПРАВЛЯЕМ СИНТАКСИС F-СТРОКИ:
                transcription_text = f"[{card.transcription}]" if card.transcription else ""

                text = f"""
    🔄 <b>Повторение</b>

    Слово: <b>{card.word_original}</b>
    {transcription_text}

    Нажмите /show чтобы увидеть перевод
                """
            else:
                text = "🎉 На сегодня все слова повторены!"

        except TelegramUser.DoesNotExist:
            text = "Сначала привяжите аккаунт командой /connect"

        self.bot.send_message(chat_id, text)