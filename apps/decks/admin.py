from django.contrib import admin
from .models import Deck, Card, UserWordProgress, StudySession

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'language', 'get_cards_count', 'is_public', 'created_at')
    list_filter = ('language', 'is_public', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('word_original', 'word_translation', 'deck', 'created_at')
    list_filter = ('deck__language', 'created_at')
    search_fields = ('word_original', 'word_translation')

@admin.register(UserWordProgress)
class UserWordProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'status', 'interval_days', 'next_review_date')
    list_filter = ('status', 'next_review_date')
    search_fields = ('user__username', 'card__word_original')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'started_at', 'ended_at', 'cards_studied', 'accuracy')
    list_filter = ('session_type', 'started_at')