from django.utils import timezone
from datetime import timedelta


def calculate_next_review(interval_days):
    """Рассчитывает дату следующего повторения"""
    return timezone.now() + timedelta(days=interval_days)


def get_today_review_cards(user):
    """Получает карточки для повторения на сегодня"""
    from .models import UserWordProgress

    return UserWordProgress.objects.filter(
        user=user,
        next_review_date__date__lte=timezone.now().date()
    ).select_related('card', 'card__deck')


def get_new_cards_for_user(user, deck=None, limit=10):
    """Получает новые карточки для пользователя"""
    from .models import Card, UserWordProgress

    # Карточки, по которым у пользователя еще нет прогресса
    if deck:
        cards = Card.objects.filter(deck=deck)
    else:
        cards = Card.objects.filter(deck__user=user)

    # Исключаем карточки, которые уже в изучении
    studied_card_ids = UserWordProgress.objects.filter(
        user=user
    ).values_list('card_id', flat=True)

    new_cards = cards.exclude(id__in=studied_card_ids)[:limit]
    return new_cards


def create_user_progress_for_card(user, card):
    """Создает запись прогресса для пользователя и карточки"""
    from .models import UserWordProgress

    progress, created = UserWordProgress.objects.get_or_create(
        user=user,
        card=card,
        defaults={
            'status': 'new',
            'next_review_date': timezone.now()
        }
    )
    return progress


def get_cards_for_study_session(user, session_type='review', limit=10):
    """Получает карточки для учебной сессии"""
    from .models import UserWordProgress, Card

    if session_type == 'review':
        # Карточки на повторение (уже есть прогресс и наступила дата повторения)
        progress_items = UserWordProgress.objects.filter(
            user=user,
            next_review_date__isnull=False,
            next_review_date__lte=timezone.now()
        ).select_related('card', 'card__deck').order_by('next_review_date')[:limit]

        return [progress.card for progress in progress_items]

    else:  # new cards
        # Новые карточки (еще нет прогресса)
        studied_card_ids = UserWordProgress.objects.filter(
            user=user
        ).values_list('card_id', flat=True)

        new_cards = Card.objects.filter(
            deck__user=user
        ).exclude(
            id__in=studied_card_ids
        )[:limit]

        return new_cards


def get_study_statistics(user):
    """Получает статистику для учебной сессии"""
    from .models import UserWordProgress, Card

    # Карточки на повторение сегодня
    review_count = UserWordProgress.objects.filter(
        user=user,
        next_review_date__isnull=False,
        next_review_date__lte=timezone.now()
    ).count()

    # Новые карточки
    studied_card_ids = UserWordProgress.objects.filter(user=user).values_list('card_id', flat=True)
    new_count = Card.objects.filter(deck__user=user).exclude(id__in=studied_card_ids).count()

    return {
        'review_count': review_count,
        'new_count': new_count
    }