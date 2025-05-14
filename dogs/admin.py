#dogs/admin.py
from django.contrib import admin
from .models import Breed, Dog
from django.utils.html import format_html  # Импортируем format_html

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Breed.

    Отображает информацию о породах собак в панели администратора Django.

    Атрибуты:
        list_display: Кортеж, определяющий поля, отображаемые в списке пород.
        search_fields: Кортеж, определяющий поля, по которым можно выполнять поиск.
        prepopulated_fields: Словарь, определяющий поля, которые автоматически заполняются на основе других полей.
    """
    list_display = ('name', 'description', 'image_preview', 'slug') # Added slug
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Added prepopulated_fields

    def image_preview(self, obj):
        """
        Отображает превью изображения породы в списке пород.

        Args:
            obj: Объект Breed.

        Returns:
            HTML-код с изображением или сообщение "(No image)", если изображение отсутствует.
        """
        if obj.image:
            return format_html('<img src="" width="100" />', obj.image.url) # Исправлена ошибка в теге img
        return '(No image)'  # Отображаем сообщение, если изображения нет
    image_preview.short_description = 'Image Preview'

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Dog.

    Отображает информацию о собаках в панели администратора Django.

    Атрибуты:
        list_display: Кортеж, определяющий поля, отображаемые в списке собак.
        search_fields: Кортеж, определяющий поля, по которым можно выполнять поиск.
        list_filter: Кортеж, определяющий поля, по которым можно фильтровать список собак.
        prepopulated_fields: Словарь, определяющий поля, которые автоматически заполняются на основе других полей.
    """
    list_display = ('name', 'breed', 'age', 'owner', 'slug') # Added slug
    search_fields = ('name',)
    list_filter = ('breed',)
    prepopulated_fields = {'slug': ('name',)} # Added prepopulated_fields
