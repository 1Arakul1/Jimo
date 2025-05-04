#dogs/admin.py
from django.contrib import admin
from .models import Breed, Dog
from django.utils.html import format_html  # Импортируем format_html

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview')
    search_fields = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="" width="100" />', obj.image.url)
        return '(No image)'  # Отображаем сообщение, если изображения нет
    image_preview.short_description = 'Image Preview'

@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'owner')
    search_fields = ('name',)
    list_filter = ('breed',)
