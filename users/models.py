# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Расширенная модель пользователя, наследующая AbstractUser.

    Добавляет дополнительные поля для хранения информации о пользователе.
    """
    # Дополнительные поля
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Номер телефона')
    is_premium = models.BooleanField(default=False, verbose_name='Премиум аккаунт')
    # Новые поля:
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Адрес')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')

    email = models.EmailField(unique=True, verbose_name='email address') # Added unique=True,  unique=True означает что поле должно быть уникальным

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_groups",  # Изменено
        related_query_name="customuser",  # Изменено
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",  # Изменено
        related_query_name="customuser",  # Изменено
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта User (username).
        """
        return self.username


class Product(models.Model):
    """
    Модель для представления продукта.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        """
        Возвращает строковое представление объекта Product (name).
        """
        return self.name