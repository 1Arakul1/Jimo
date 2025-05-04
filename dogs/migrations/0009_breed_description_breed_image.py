from django.db import migrations, models
from django.core.files import File
from django.conf import settings
import os

def populate_breed_images(apps, schema_editor):
    Breed = apps.get_model('dogs', 'Breed')
    breed_image_data = {
        'Лабрадор ретривер': 'breed_images/labrador.jpg',
        'Немецкая овчарка': 'breed_images/german_shepherd.jpg',
        'Французский бульдог': 'breed_images/french_bulldog.jpeg',
        'Золотистый ретривер': 'breed_images/golden_retriever.jpg',
        'Бульдог': 'breed_images/bulldog.jpg',
        'Пудель': 'breed_images/poodle.jpg',
    }

    for breed_name, image_path in breed_image_data.items():
        try:
            breed = Breed.objects.get(name=breed_name)
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(full_image_path):
                with open(full_image_path, 'rb') as f:
                    file = File(f)
                    print(f"Сохраняем изображение для {breed_name} из {full_image_path}") # Added print
                    breed.image.save(os.path.basename(image_path), file, save=False)
                breed.save()
                print(f"Изображение для породы '{breed_name}' установлено: {breed.image.url}")  # Добавлено
            else:
                print(f"Файл изображения не найден: {full_image_path}")

        except Breed.DoesNotExist:
            print(f"Порода '{breed_name}' не найдена.")

    for breed_name, image_path in breed_image_data.items():
        try:
            breed = Breed.objects.get(name=breed_name)
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(full_image_path):
                with open(full_image_path, 'rb') as f:  # Открываем файл для чтения в бинарном режиме
                    file = File(f)
                    breed.image.save(os.path.basename(image_path), file, save=False)  # Сохраняем изображение
                breed.save()  # Сохраняем модель с изображением
            else:
                print(f"Файл изображения не найден: {full_image_path}")

        except Breed.DoesNotExist:
            print(f"Порода '{breed_name}' не найдена.")

def reverse_populate_breed_images(apps, schema_editor):
    Breed = apps.get_model('dogs', 'Breed')
    for breed_name in [
        'Лабрадор ретривер',
        'Немецкая овчарка',
        'Французский бульдог',
        'Золотистый ретривер',
        'Бульдог',
        'Пудель',
    ]:
        try:
            breed = Breed.objects.get(name=breed_name)
            # You may want to delete the image files here as well
            breed.image.delete(save=False) #Delete image file
            breed.image = None #set image to None
            breed.save()
        except Breed.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0008_dog_birth_date'),  # Замените на номер предыдущей миграции
    ]

    operations = [
         migrations.AddField(
            model_name='breed',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание породы'),
        ),
        migrations.AddField(
            model_name='breed',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='breed_images/', verbose_name='Изображение породы'),
        ),
        migrations.RunPython(populate_breed_images, reverse_populate_breed_images),
    ]
