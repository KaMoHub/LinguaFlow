from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.decks.urls')),  # Главная страница и дашборд
    path('users/', include('apps.users.urls')),  # Авторизация и профиль
    path('telegram/', include('telegram_bot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)