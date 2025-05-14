#dogs\forms.py
from django import forms
from .models import Dog, Pedigree, Review  
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory
from .models import Dog, Pedigree, Review

class DogForm(forms.ModelForm):
    """
    Форма для создания и редактирования данных о собаке.

    Поля:
        - name: Имя собаки.
        - breed: Порода собаки.
        - age: Возраст собаки.
        - description: Описание собаки.
        - image: Изображение собаки.
        - birth_date: Дата рождения собаки.

    Виджеты:
        - birth_date:  Отображается как поле для выбора даты (type="date").
    """
    class Meta:
        model = Dog
        fields = ['name', 'breed', 'age', 'description', 'image', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ReviewForm(forms.ModelForm):
    """
    Форма для создания отзыва о собаке.

    Поля:
        - text: Текст отзыва.
        - rating: Рейтинг отзыва (от 1 до 5).

    Виджеты:
        - text: Текстовая область для ввода текста отзыва.
        - rating: Числовое поле для ввода рейтинга с ограничениями min=1 и max=5.
    """
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

class ReviewUpdateForm(forms.ModelForm):
    """
    Форма для редактирования отзыва о собаке.

    Поля:
        - text: Текст отзыва.
        - rating: Рейтинг отзыва (от 1 до 5).

    Виджеты:
        - text: Текстовая область для ввода текста отзыва.
        - rating: Числовое поле для ввода рейтинга с ограничениями min=1 и max=5.
    """
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

PedigreeFormSet = inlineformset_factory(Dog, Pedigree,
                                        fields=('father', 'mother', 'grand_father_father',
                                                'grand_mother_father', 'grand_father_mother',
                                                'grand_mother_mother'),
                                        extra=1, can_delete=True)


class DogForm(forms.ModelForm):
    """
    Форма для создания и редактирования данных о собаке.  Дубликат, возможно, удалить.

    Поля:
        - name: Имя собаки.
        - breed: Порода собаки.
        - age: Возраст собаки.
        - description: Описание собаки.
        - image: Изображение собаки.
        - birth_date: Дата рождения собаки.

    Виджеты:
        - birth_date:  Отображается как поле для выбора даты (type="date").
    """
    class Meta:
        model = Dog
        fields = ['name', 'breed', 'age', 'description', 'image',
                  'birth_date'] 
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  
        }


class ReviewForm(forms.ModelForm):
    """
    Форма для создания отзыва о собаке.  Дубликат, возможно, удалить.

    Поля:
        - text: Текст отзыва.
        - rating: Рейтинг отзыва (от 1 до 5).

    Виджеты:
        - text: Текстовая область для ввода текста отзыва.
        - rating: Числовое поле для ввода рейтинга с ограничениями min=1 и max=5.
    """
    class Meta:
        model = Review
        fields = ['text', 'rating'] # Remove 'dog'
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            #'dog': forms.HiddenInput(),  # Скрываем поле dog
        }



class ReviewUpdateForm(forms.ModelForm):
    """
    Форма для редактирования отзыва о собаке.  Дубликат, возможно, удалить.

    Поля:
        - text: Текст отзыва.
        - rating: Рейтинг отзыва (от 1 до 5).

    Виджеты:
        - text: Текстовая область для ввода текста отзыва.
        - rating: Числовое поле для ввода рейтинга с ограничениями min=1 и max=5.
    """
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }