from django.core.management.base import BaseCommand
from apps.decks.models import Card
from utils.text_to_speech import generate_audio_for_card
from django.conf import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Исправляет привязку аудио файлов для существующих карточек'

    def handle(self, *args, **options):
        # Все карточки
        cards = Card.objects.all()

        self.stdout.write(f'Найдено {cards.count()} карточек для проверки')

        fixed_count = 0
        for card in cards:
            self.stdout.write(f'Проверка карточки {card.id}: {card.word_original}')

            # Если аудио не привязано, но файл существует
            if not card.audio_original:
                expected_path = f'audio/original/card_{card.id}_original.mp3'
                full_path = Path(settings.MEDIA_ROOT) / expected_path

                if full_path.exists():
                    # Привязываем существующий файл
                    card.audio_original.name = expected_path
                    card.save()
                    self.stdout.write(f'✓ Исправлена карточка {card.id}')
                    fixed_count += 1
                else:
                    # Генерируем аудио заново
                    card_with_audio = generate_audio_for_card(card)
                    if card_with_audio.audio_original:
                        card.audio_original = card_with_audio.audio_original
                        card.audio_translation = card_with_audio.audio_translation
                        card.audio_example = card_with_audio.audio_example
                        card.save()
                        self.stdout.write(f'✓ Перегенерировано для карточки {card.id}')
                        fixed_count += 1
                    else:
                        self.stdout.write(f'✗ Ошибка для карточки {card.id}')
            else:
                self.stdout.write(f'✓ Карточка {card.id} уже имеет аудио')

        self.stdout.write(f'Исправлено карточек: {fixed_count}')