# users/views_reset_password.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .forms import PasswordResetRequestForm
import secrets
import string
from django.utils.html import format_html

User = get_user_model()

def generate_random_password(length=12):
    """
    Генерирует случайный пароль заданной длины, состоящий только из букв и цифр.

    Args:
        length (int): Длина пароля.

    Returns:
        str: Сгенерированный пароль.
    """
    alphabet = string.ascii_letters + string.digits # Only letters and digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def password_reset_request(request):
    """
    Представление для запроса сброса пароля.

    Обрабатывает отправку формы PasswordResetRequestForm, генерирует новый пароль,
    отправляет его пользователю по электронной почте и перенаправляет на страницу входа.

    Args:
        request: Объект запроса.

    Returns:
        HttpResponse: Отображает форму запроса сброса пароля или перенаправляет
                      на страницу входа с сообщением об успехе.
    """
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Пользователь с таким email не найден.")
                return render(request, 'users/password_reset_request.html', {'form': form})

            new_password = generate_random_password()
            user.set_password(new_password)
            user.save()

            subject = "Ваш новый пароль"
            message = format_html(
                "<p>Здравствуйте, {}!</p>"
                "<p>Ваш пароль был сброшен. Ваш новый пароль: <strong>{}</strong></p>"
                "<p>Пожалуйста, смените пароль после входа в систему.</p>",
                user.username,
                new_password
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False) # Добавил fail_silently

            messages.success(request, "Новый пароль отправлен на ваш email.")
            return redirect('users:user_login')  # Перенаправляем на страницу входа
        else:
            messages.error(request, "Пожалуйста, введите корректный email.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})