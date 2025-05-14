#0005_remove_breed_description_alter_breed_name.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0004_alter_breed_options_alter_dog_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='breed',
            name='description',
        ),
        migrations.AlterField(
            model_name='breed',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название породы'),
        ),
    ]
