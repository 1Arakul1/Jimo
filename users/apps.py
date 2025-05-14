#users\apps.py
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения 'users'.

    Атрибуты:
        default_auto_field: Тип автоматического первичного ключа по умолчанию.
        name: Имя приложения.
        verbose_name: Отображаемое имя приложения (на русском языке).

    Методы:
        ready(): Вызывается при запуске приложения.  Импортирует модуль signals для регистрации сигналов.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        """
        Вызывается при запуске приложения.

        Импортирует модуль signals для регистрации сигналов.
        """
        import users.signals  # Импортируем модуль signals