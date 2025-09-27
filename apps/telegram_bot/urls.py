from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('connect/', views.connect_telegram, name='connect'),
    path('unlink/', views.unlink_telegram, name='unlink'),
    path('info/', views.bot_info, name='bot_info'),
]