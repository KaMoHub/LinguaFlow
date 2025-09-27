from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('decks/', views.deck_list, name='deck_list'),
    path('decks/create/', views.deck_create, name='deck_create'),
    path('decks/<int:deck_id>/', views.deck_detail, name='deck_detail'),
    path('decks/<int:deck_id>/add-card/', views.card_create, name='card_create'),
    path('review/', views.review, name='review'),
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('card/<int:card_id>/edit/', views.card_edit, name='card_edit'),
    path('card/<int:card_id>/delete/', views.card_delete, name='card_delete'),
]