from django.db import migrations
from django.contrib.auth.hashers import make_password


def populate_breeds(apps, schema_editor):
    Breed = apps.get_model('dogs', 'Breed')

    breeds_data = [
        {
            'name': 'Лабрадор ретривер',
        },
        {
            'name': 'Немецкая овчарка',
        },
        {
            'name': 'Французский бульдог',
        },
        {
            'name': 'Золотистый ретривер',
        },
        {
            'name': 'Бульдог',
        },
        {
            'name': 'Пудель',
        },
    ]

    for breed_data in breeds_data:
        breed = Breed(name=breed_data['name'])
        breed.save()

def populate_dogs(apps, schema_editor):
    Dog = apps.get_model('dogs', 'Dog')
    Breed = apps.get_model('dogs', 'Breed')
    User = apps.get_model('users', 'User')  # Использовать users.User

    # Получаем существующие породы
    labrador = Breed.objects.get(name='Лабрадор ретривер')
    german_shepherd = Breed.objects.get(name='Немецкая овчарка')
    french_bulldog = Breed.objects.get(name='Французский бульдог')
    golden_retriever = Breed.objects.get(name='Золотистый ретривер')
    bulldog = Breed.objects.get(name='Бульдог')
    poodle = Breed.objects.get(name='Пудель')

    # Получаем или создаем пользователя admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            password='password',  # Укажите надежный пароль
            email='admin@example.com'  # Укажите адрес электронной почты
        )


    # Создаем примеры собак
    dogs_data = [
        {
            'name': 'Бадди',
            'breed': labrador,
            'age': 3,
            'description': 'Дружелюбный и энергичный, отличный компаньон.',
            'image': 'dog_images/labrador.jpg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
        {
            'name': 'Рекс',
            'breed': german_shepherd,
            'age': 5,
            'description': 'Умный, преданный и бдительный защитник.',
            'image': 'dog_images/german_shepherd.jpg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
        {
            'name': 'Пирожок',
            'breed': french_bulldog,
            'age': 2,
            'description': 'Компактный и дружелюбный, отличный выбор для квартиры.',
            'image': 'dog_images/french_bulldog.jpeg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
        {
            'name': 'Чарли',
            'breed': golden_retriever,
            'age': 4,
            'description': 'Добродушный и преданный, отличный компаньон для семьи.',
            'image': 'dog_images/golden_retriever.jpg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
        {
            'name': 'Бутч',
            'breed': bulldog,
            'age': 6,
            'description': 'Спокойный и дружелюбный, любит проводить время с хозяином.',
            'image': 'dog_images/bulldog.jpg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
        {
            'name': 'Кудряшка',
            'breed': poodle,
            'age': 1,
            'description': 'Умный и элегантный, гипоаллергенный компаньон.',
            'image': 'dog_images/poodle.jpg',  # Укажите путь к изображению
            #'owner': admin,  # Не назначаем владельца
        },
    ]

    for dog_data in dogs_data:
        dog = Dog(
            name=dog_data['name'],
            breed=dog_data['breed'],
            age=dog_data['age'],
            description=dog_data['description'],
            image=dog_data['image'],
            #owner = dog_data['owner']  # Не назначаем владельца
        )
        dog.save()



def reverse_populate_breeds(apps, schema_editor):
    Breed = apps.get_model('dogs', 'Breed')
    for breed_data in [
        {'name': 'Лабрадор ретривер'},
        {'name': 'Немецкая овчарка'},
        {'name': 'Французский бульдог'},
        {'name': 'Золотистый ретривер'},
        {'name': 'Бульдог'},
        {'name': 'Пудель'},
    ]:
        try:
            breed = Breed.objects.get(name=breed_data['name'])
            breed.delete()
        except Breed.DoesNotExist:
            pass

def reverse_populate_dogs(apps, schema_editor):
    Dog = apps.get_model('dogs', 'Dog')
    for dog_data in [
        {'name': 'Бадди'},
        {'name': 'Рекс'},
        {'name': 'Пирожок'},
        {'name': 'Чарли'},
        {'name': 'Бутч'},
        {'name': 'Кудряшка'},
    ]:
        try:
            dog = Dog.objects.get(name=dog_data['name'])
            dog.delete()
        except Dog.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0008_add_owner_to_dog'),
    ]

    operations = [
        migrations.RunPython(populate_breeds, reverse_populate_breeds),
        migrations.RunPython(populate_dogs, reverse_populate_dogs)
    ]