import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .services import handle_telegram_update # Импортируем функцию из services.py

logger = logging.getLogger(__name__)

@csrf_exempt # Вебхук от Telegram будет POST-запросом без CSRF токена
@require_POST # Разрешаем только POST-запросы
def telegram_webhook(request):
    """
    Обрабатывает POST-запросы от Telegram.
    """
    try:
        # Получаем JSON-данные из тела запроса
        update_data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Получено обновление от Telegram: {update_data}")

        # Передаём данные в основную логику обработки
        handle_telegram_update(update_data)

        # Возвращаем пустой ответ с кодом 200 OK
        # Telegram интерпретирует 200 как успешно обработанный запрос
        # и не будет отправлять его повторно.
        return HttpResponse(status=200)

    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON из запроса от Telegram.")
        return HttpResponse(status=400) # Bad Request
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}")
        return HttpResponse(status=500) # Internal Server Error

# views.py