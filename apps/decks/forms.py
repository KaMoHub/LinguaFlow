from django import forms
from .models import Deck, Card

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name', 'description', 'language', 'cover_image', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Название набора'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Описание набора',
                'rows': 3
            }),
            'language': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['word_original', 'word_translation', 'transcription', 'example_sentence', 'image_url']
        widgets = {
            'word_original': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Слово на иностранном языке'
            }),
            'word_translation': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Перевод'
            }),
            'transcription': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Транскрипция (опционально)'
            }),
            'example_sentence': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Пример использования',
                'rows': 2
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ссылка на изображение (опционально)'
            }),
        }

class CardEditForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['word_original', 'word_translation', 'transcription', 'example_sentence', 'image_url']
        widgets = {
            'word_original': forms.TextInput(attrs={'class': 'form-control'}),
            'word_translation': forms.TextInput(attrs={'class': 'form-control'}),
            'transcription': forms.TextInput(attrs={'class': 'form-control'}),
            'example_sentence': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
        }