from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    User = get_user_model()

    if User.objects.filter(username='admin').exists():
        return

    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print('Создан суперпользователь admin с паролем password')