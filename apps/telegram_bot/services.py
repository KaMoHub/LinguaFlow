import logging
from telegram import Update # Импортируем Update для проверки типа данных
from telegram.ext import Application, ContextTypes # Импортируем Application и ContextTypes
from django.conf import settings
from .models import TelegramUser, BotMessage

logger = logging.getLogger(__name__)

# --- Создаём Application (обычно это делается один раз на старте бота, но мы можем создать его тут для доступа к bot) ---
# Однако, для вебхуков, мы создаём Application, чтобы получить объект bot для отправки сообщений.
# В идеале, это нужно сделать один раз при старте Django приложения, а не при каждом вызове.
# Но для простоты пока оставим тут, хотя это не оптимально.
# Лучше использовать Application.job_queue для планирования задач или передавать bot извне.

# Создаём ApplicationBuilder и получаем Application
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
bot = application.bot # Получаем объект bot из application

# --- Функции обработки ---
# Эти функции НЕ должны быть асинхронными (async def), потому что вызываются из views.py синхронно.
# Мы используем sync_to_async внутри, если нужно выполнить ORM-запросы.
# Но для простоты и уменьшения сложности в этом примере, пока оставим синхронными.
# Потенциальная проблема: ORM запросы блокируют поток обработки вебхука.

def handle_telegram_update(update_data):
    """
    Основная функция обработки обновления от Telegram.
    """
    try:
        # telegram.ext.Update.from_dict() - это альтернатива Update.de_json, но требует application.
        # update = Update.de_json(update_data) # Старый способ, может не всегда корректно работать с новыми полями
        # Проще передать update_data как есть в handle_message и там распаковать нужные поля.
        # Однако, для доступа к полям типа .message, .callback_query, лучше всё-таки создать объект Update.
        # В новой версии нужно использовать Application для создания Update, но в контексте вебхука это неудобно.
        # Вместо этого, будем работать с update_data как с dict.

        # Проверяем, есть ли сообщение
        if 'message' in update_data:
            handle_message(update_data['message'])
        elif 'callback_query' in update_data:
            handle_callback_query(update_data['callback_query'])
        # Добавьте другие типы обновлений, если нужно (inline_query, chosen_inline_result, shipping_query, pre_checkout_query)
        else:
            logger.info(f"Получен тип обновления, не требующий специальной обработки: {update_data.keys()}")

    except Exception as e:
        logger.error(f"Ошибка в handle_telegram_update: {e}")


def handle_message(message_data):
    """
    Обрабатывает входящее сообщение из update_data.
    """
    chat_id = message_data['chat']['id']
    text = message_data.get('text', '') # Используем .get() на случай, если текста нет (например, фото с подписью)
    user_data = message_data['from']
    user_id = user_data['id']
    username = user_data.get('username', '') # Может быть None
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')

    logger.info(f"Получено сообщение от {user_id} ({username}): {text}")

    # Сохраняем сообщение в лог (BotMessage)
    BotMessage.objects.create(
        telegram_id=chat_id,
        message_text=text,
        command=text.split()[0] if text.startswith('/') else "", # Сохраняем команду, если это команда
    )

    # Получаем или создаем TelegramUser
    telegram_user, created = TelegramUser.objects.get_or_create(
        telegram_id=user_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    if created:
        logger.info(f"Создан новый пользователь Telegram: {telegram_user}")
    else:
        # Обновляем данные пользователя, если они изменились
        updated = False
        if telegram_user.username != username:
            telegram_user.username = username
            updated = True
        if telegram_user.first_name != first_name:
            telegram_user.first_name = first_name
            updated = True
        if telegram_user.last_name != last_name:
            telegram_user.last_name = last_name
            updated = True
        if updated:
            telegram_user.save()

    # --- Основная логика обработки сообщений ---
    # Здесь вы реализуете, что должен делать бот.
    # Пример: обработка команд и простого текста
    if text == '/start':
        response_text = f"Привет, {first_name}! Добро пожаловать в LinguaFlow!"
        # Используем объект bot для отправки сообщения
        bot.send_message(chat_id=chat_id, text=response_text)
        # Сохраняем ответ в лог
        BotMessage.objects.create(telegram_id=chat_id, response_text=response_text)
    elif text.startswith('/'):
        # Обработка других команд
        response_text = f"Команда '{text.split()[0]}' пока не реализована."
        bot.send_message(chat_id=chat_id, text=response_text)
        BotMessage.objects.create(telegram_id=chat_id, response_text=response_text)
    else:
        # Обработка обычного текста
        response_text = f"Вы сказали: {text}. Я пока не умею отвечать на произвольный текст, но могу обрабатывать команды. Попробуйте /start."
        bot.send_message(chat_id=chat_id, text=response_text)
        BotMessage.objects.create(telegram_id=chat_id, response_text=response_text)


def handle_callback_query(callback_query_data):
    """
    Обрабатывает callback query (например, от inline клавиатур) из update_data.
    """
    query_id = callback_query_data['id']
    chat_id = callback_query_data['message']['chat']['id'] # или 'from' для пользователя, но чаще используют chat
    data = callback_query_data['data']

    logger.info(f"Получен callback_query с данными: {data}")

    # Ваша логика обработки данных callback_query
    # Например, обновление состояния пользователя, отправка нового сообщения и т.д.

    # Ответим Telegram, что запрос обработан
    bot.answer_callback_query(query_id, text="Callback обработан!")
    # Обратите внимание: bot.answer_callback_query не возвращает Future, поэтому await не нужен, даже если бы функция была async.

# services.py