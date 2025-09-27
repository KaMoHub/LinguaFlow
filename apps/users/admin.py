from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'daily_new_cards_limit', 'current_streak', 'last_study_date')
    list_filter = ('daily_new_cards_limit', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('LinguaFlow Settings', {
            'fields': ('daily_new_cards_limit', 'current_streak', 'last_study_date', 'avatar')
        }),
    )