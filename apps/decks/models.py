from django.db import models
from apps.core.models import TimeStampedModel
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Deck(TimeStampedModel):
    """Модель набора слов"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese'),
        ('ru', 'Russian'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    cover_image = models.ImageField(upload_to='deck_covers/', null=True, blank=True)
    is_public = models.BooleanField(default=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='decks')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

    def get_cards_count(self):
        return self.cards.count()

    def get_new_cards_count(self, user):
        """Количество новых карточек для пользователя"""
        return self.cards.exclude(
            progress__user=user,
            progress__status__in=['learning', 'review', 'mastered']
        ).count()


class Card(TimeStampedModel):
    """Модель карточки слова"""
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    word_original = models.CharField(max_length=200)
    word_translation = models.CharField(max_length=200)
    transcription = models.CharField(max_length=200, blank=True)
    example_sentence = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    # Аудио файлы
    audio_original = models.FileField(upload_to='audio/original/', null=True, blank=True)
    audio_translation = models.FileField(upload_to='audio/translation/', null=True, blank=True)
    audio_example = models.FileField(upload_to='audio/example/', null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.word_original} - {self.word_translation}"

    def save(self, *args, **kwargs):
        from utils.text_to_speech import generate_audio_for_card

        is_new = self.pk is None

        # Сохраняем карточку первый раз, чтобы получить ID
        super().save(*args, **kwargs)

        # Генерируем аудио для новой карточки
        if is_new:
            try:
                logger.info(f"Начинаем генерацию аудио для карточки {self.id}")

                # Генерируем аудио
                card_with_audio = generate_audio_for_card(self)

                # Сохраняем карточку с обновленными путями к аудио
                if card_with_audio.audio_original:
                    logger.info(f"Аудио сгенерировано, сохраняем карточку {self.id}")
                    super().save(update_fields=[
                        'audio_original',
                        'audio_translation',
                        'audio_example'
                    ])
                else:
                    logger.warning(f"Аудио не было сгенерировано для карточки {self.id}")

            except Exception as e:
                logger.error(f"Ошибка при генерации аудио для карточки {self.id}: {e}")


class UserWordProgress(models.Model):
    """Прогресс пользователя по конкретному слову"""
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('learning', 'Изучается'),
        ('review', 'На повторении'),
        ('mastered', 'Выучено'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='progress')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='progress')

    interval_days = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    repetition_count = models.IntegerField(default=0)

    next_review_date = models.DateTimeField(null=True, blank=True)
    last_review_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    correct_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'card']
        ordering = ['next_review_date']

    @property
    def accuracy(self):
        return (self.correct_count / self.total_count * 100) if self.total_count > 0 else 0

    def update_progress(self, quality):
        """Обновление прогресса по алгоритму SuperMemo-2 с качеством ответа"""
        from datetime import timedelta

        # Качество ответа: 0-5 (0 - полное незнание, 5 - идеально)
        # В нашем интерфейсе будет: 1-Сложно, 3-Нормально, 5-Легко

        if quality >= 3:  # Правильный ответ
            if self.repetition_count == 0:
                self.interval_days = 1
            elif self.repetition_count == 1:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)

            self.repetition_count += 1
        else:  # Неправильный ответ
            self.interval_days = 1
            self.repetition_count = 0

        # Обновление фактора легкости по формуле SuperMemo-2
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        # Расчет следующей даты повторения
        self.next_review_date = timezone.now() + timedelta(days=self.interval_days)
        self.last_review_date = timezone.now()

        # Обновление статуса
        if self.interval_days >= 21:  # Если интервал больше 21 дня - слово выучено
            self.status = 'mastered'
        elif self.repetition_count > 0:
            self.status = 'review'
        else:
            self.status = 'learning'

        self.total_count += 1
        if quality >= 3:
            self.correct_count += 1

        self.save()


class StudySession(TimeStampedModel):
    """Статистика по сессии изучения"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    cards_studied = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    session_type = models.CharField(max_length=10, choices=[('new', 'Новые'), ('review', 'Повторение')])

    @property
    def duration_minutes(self):
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return 0

    @property
    def accuracy(self):
        return (self.correct_answers / self.cards_studied * 100) if self.cards_studied > 0 else 0