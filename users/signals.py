#users\signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """
    Сигнал для создания суперпользователя при миграции базы данных.

    Этот сигнал срабатывает после выполнения всех миграций для приложения.
    Он проверяет, существует ли пользователь с именем 'admin'.
    Если нет, то создается суперпользователь с указанными данными.

    Args:
        sender:  Класс отправителя сигнала (обычно приложение).
        **kwargs:  Словарь с дополнительными аргументами.
    """
    User = get_user_model()

    if User.objects.filter(username='admin').exists():
        return

    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print('Создан суперпользователь admin с паролем password')