# dogs\migrations\0014_breed_slug_dog_slug_review_updated_at.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0013_alter_review_options_remove_dog_active_and_more'),  # Замени на номер предыдущей миграции
    ]

    operations = [
        migrations.AddField(
            model_name='breed',
            name='slug',
            field=models.SlugField(max_length=255, blank=True, null=True),  # Разрешаем NULL
        ),
        migrations.AddField(
            model_name='dog',
            name='slug',
            field=models.SlugField(max_length=255, blank=True, null=True),  # Разрешаем NULL
        ),
       migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]