# users/views.py
# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import LoginForm, RegisterForm, EditProfileForm, PasswordResetRequestForm
from dogs.models import Dog
import secrets
import string
from users.models import User
from django.views.generic import TemplateView, UpdateView, FormView, RedirectView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # LoginRequiredMixin для классов
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template import Context, Template
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required, user_passes_test # Импортируем декораторы
from django.contrib.auth.models import Permission


class UserDetailView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения детальной информации о пользователе.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        TemplateView:  Базовый класс для представлений, отображающих шаблон.

    Атрибуты:
        template_name (str): Путь к шаблону для отображения информации о пользователе.

    Методы:
        get_context_data(**kwargs):  Получает контекст для отображения шаблона,
                                      включая информацию о просматриваемом пользователе и его собаках.
    """
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        """
        Получает контекст для отображения детальной информации о пользователе.

        Args:
            **kwargs:  Словарь дополнительных аргументов.

        Returns:
            dict: Словарь контекста, содержащий информацию о просматриваемом пользователе
                  и его собаках.
        """
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        context['viewed_user'] = get_object_or_404(User, pk=user_id)
        context['dogs'] = Dog.objects.filter(owner=context['viewed_user'])
        return context

# --- User Authentication Views ---

class UserLoginView(FormView):
    """
    Представление для входа пользователя в систему.

    Наследует:
        FormView: Базовый класс для представлений, обрабатывающих формы.

    Атрибуты:
        form_class: Класс формы для входа.
        template_name: Путь к шаблону для отображения формы входа.

    Методы:
        form_valid(form):  Обрабатывает успешную отправку формы, выполняет аутентификацию
                          и вход пользователя в систему.
        form_invalid(form):  Обрабатывает неверные данные формы, отображает сообщение об ошибке.
    """
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы входа.

        Args:
            form:  Объект формы.

        Returns:
            HttpResponseRedirect:  Перенаправляет пользователя на страницу приветствия
                                    в случае успешного входа, иначе отображает форму с ошибкой.
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(reverse_lazy('users:welcome'))
        else:
            messages.error(self.request, 'Неверное имя пользователя или пароль')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверные данные формы входа.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse: Отображает форму с ошибками.
        """
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return self.render_to_response(self.get_context_data(form=form))


class RegisterView(FormView):
    """
    Представление для регистрации нового пользователя.

    Наследует:
        FormView: Базовый класс для представлений, обрабатывающих формы.

    Атрибуты:
        form_class: Класс формы для регистрации.
        template_name: Путь к шаблону для отображения формы регистрации.

    Методы:
        form_valid(form):  Обрабатывает успешную отправку формы, создает пользователя,
                          отправляет письмо подтверждения и выполняет вход в систему.
        form_invalid(form):  Обрабатывает неверные данные формы, отображает сообщение об ошибке.
    """
    form_class = RegisterForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы регистрации.

        Args:
            form: Объект формы.

        Returns:
            HttpResponseRedirect:  Перенаправляет пользователя на страницу приветствия
                                    в случае успешной регистрации, иначе отображает форму с ошибкой.
        """
        try:
            user = form.save()
            # Send confirmation email
            subject = 'Добро пожаловать в наш питомник!'
            message = f'Здравствуйте, {user.username}!\n\nСпасибо за регистрацию в нашем питомнике.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            email = EmailMessage(subject, message, from_email, recipient_list)
            email.fail_silently = False
            email.send()

            messages.success(self.request, "Вы успешно зарегистрировались и вошли в систему!")
            login(self.request, user)
            return HttpResponseRedirect(reverse_lazy('users:welcome'))
        except Exception as e:
            error_message = f"Ошибка при отправке письма: {type(e).__name__} - {str(e)}"
            messages.error(self.request, f"Ошибка при регистрации: {error_message}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверные данные формы регистрации.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse: Отображает форму с ошибками.
        """
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(RedirectView):
    """
    Представление для выхода пользователя из системы.

    Наследует:
        RedirectView:  Базовый класс для представлений, выполняющих перенаправление.

    Атрибуты:
        url: URL для перенаправления после выхода.

    Методы:
        get(request, *args, **kwargs):  Выполняет выход пользователя и перенаправляет на указанный URL.
    """
    url = reverse_lazy('users:logout_success')

    def get(self, request, *args, **kwargs):
        """
        Выполняет выход пользователя из системы.

        Args:
            request: Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponseRedirect:  Перенаправляет на URL после выхода.
        """
        django_logout(request)
        return super().get(request, *args, **kwargs)


class LogoutSuccessView(TemplateView):
    """
    Представление для отображения сообщения об успешном выходе из системы.

    Наследует:
        TemplateView:  Базовый класс для представлений, отображающих шаблон.

    Атрибуты:
        template_name:  Путь к шаблону для отображения сообщения об успешном выходе.

    Методы:
        get(request, *args, **kwargs):  Отображает шаблон.
    """
    template_name = 'users/logout_success.html'

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения страницы успешного выхода.

        Args:
            request: Объект запроса.
            *args:  Дополнительные позиционные аргументы.
            **kwargs:  Дополнительные именованные аргументы.

        Returns:
            HttpResponse:  Отображает шаблон страницы успешного выхода.
        """
        return super().get(request, *args, **kwargs)


class WelcomeView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения страницы приветствия для авторизованных пользователей.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        TemplateView:  Базовый класс для представлений, отображающих шаблон.

    Атрибуты:
        template_name:  Путь к шаблону для отображения страницы приветствия.

    Методы:
        get(request, *args, **kwargs):  Отображает шаблон.
    """
    template_name = 'users/welcome.html'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения страницы приветствия.

        Args:
            request: Объект запроса.
            *args:  Дополнительные позиционные аргументы.
            **kwargs:  Дополнительные именованные аргументы.

        Returns:
            HttpResponse:  Отображает шаблон страницы приветствия.
        """
        return super().get(request, *args, **kwargs)


# --- User Profile Views ---

class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения профиля пользователя.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        TemplateView:  Базовый класс для представлений, отображающих шаблон.

    Атрибуты:
        template_name:  Путь к шаблону для отображения профиля.

    Методы:
        get_context_data(self, **kwargs):  Получает контекст для отображения шаблона,
                                          включая информацию о пользователе и его собаках.
    """
    template_name = 'users/user_profile.html'

    def get_context_data(self, **kwargs):
        """
        Получает контекст для отображения профиля пользователя.

        Args:
            **kwargs:  Словарь дополнительных аргументов.

        Returns:
            dict: Словарь контекста, содержащий информацию о пользователе, его собаках,
                  и флаг, указывающий, является ли пользователь суперпользователем.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        context['user'] = self.request.user
        context['dogs'] = Dog.objects.filter(owner=self.request.user)
        context['is_superuser'] = self.request.user.is_superuser
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля пользователя.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        UpdateView:  Базовый класс для представлений, обновляющих существующие объекты.

    Атрибуты:
        form_class: Класс формы для редактирования профиля.
        template_name:  Путь к шаблону для отображения формы редактирования профиля.
        success_url: URL для перенаправления после успешного обновления профиля.

    Методы:
        get_object():  Возвращает объект пользователя, который будет редактироваться.
        form_valid(form):  Обрабатывает успешную отправку формы, отображает сообщение об успехе.
        form_invalid(form):  Обрабатывает неверные данные формы, отображает сообщение об ошибке.
    """
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:user_profile')

    def get_object(self):
        """
        Возвращает объект пользователя, который будет редактироваться.

        Returns:
            User:  Объект текущего пользователя.
        """
        return self.request.user

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы редактирования профиля.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse:  Отображает страницу профиля с сообщением об успехе.
        """
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверные данные формы редактирования профиля.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse:  Отображает форму с ошибками.
        """
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    Представление для изменения пароля пользователя.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        FormView:  Базовый класс для представлений, обрабатывающих формы.

    Атрибуты:
        form_class: Класс формы для изменения пароля.
        template_name:  Путь к шаблону для отображения формы изменения пароля.
        success_url: URL для перенаправления после успешного изменения пароля.

    Методы:
        get_form_kwargs():  Передает текущего пользователя в форму.
        form_valid(form):  Обрабатывает успешную отправку формы, обновляет сессию пользователя.
    """
    form_class = PasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:user_profile')

    def get_form_kwargs(self):
        """
        Передает текущего пользователя в форму.

        Returns:
            dict: Словарь, содержащий аргументы для инициализации формы.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы изменения пароля.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse:  Отображает страницу профиля с сообщением об успехе.
        """
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)


# --- Password Reset Views ---

class PasswordResetRequestView(FormView):
    """
    Представление для запроса сброса пароля.

    Наследует:
        FormView: Базовый класс для представлений, обрабатывающих формы.

    Атрибуты:
        form_class: Класс формы для запроса сброса пароля.
        template_name: Путь к шаблону для отображения формы запроса сброса пароля.
        success_url:  URL для перенаправления после успешного запроса сброса пароля.

    Методы:
        form_valid(form):  Обрабатывает успешную отправку формы, генерирует новый пароль,
                          отправляет письмо с новым паролем и перенаправляет пользователя.
        form_invalid(form):  Обрабатывает неверные данные формы, отображает сообщение об ошибке.
    """
    form_class = PasswordResetRequestForm
    template_name = 'users/password_reset_request.html'
    success_url = reverse_lazy('users:user_login')  # Redirect to login after reset

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы запроса сброса пароля.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse:  Перенаправляет пользователя на страницу входа
                          с сообщением об отправке нового пароля.
        """
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с таким email не найден.")
            return self.form_invalid(form)

        # Generate a new random password
        new_password = generate_random_password()
        user.set_password(new_password)  # Hash the password
        user.password_reset_token = None  # Очищаем токен, если он использовался
        user.save()

        # Send email with the new password
        subject = 'Ваш новый пароль'
        html_message = render_to_string(
            'users/password_reset_email.html',  # Создайте новый шаблон или используйте plain text
            {'user': user, 'new_password': new_password}
        )
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        messages.success(self.request, "Новый пароль отправлен на ваш email.")
        return HttpResponseRedirect(self.success_url)  # Redirect to login

    def form_invalid(self, form):
        """
        Обрабатывает неверные данные формы запроса сброса пароля.

        Args:
            form: Объект формы.

        Returns:
            HttpResponse:  Отображает форму с ошибками.
        """
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return self.render_to_response(self.get_context_data(form=form))


# --- User Management Views (Superuser Only) ---

class UserListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка пользователей (доступно только суперпользователям).

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        ListView:  Базовый класс для представлений, отображающих списки объектов.

    Атрибуты:
        model: Модель данных для отображения (User).
        template_name:  Путь к шаблону для отображения списка пользователей.
        context_object_name:  Имя, под которым список пользователей будет доступен в шаблоне.
        paginate_by: Количество объектов на странице.

    Методы:
        get_queryset():  Возвращает QuerySet пользователей, включая фильтрацию по поисковому запросу.
        get_context_data(**kwargs):  Добавляет в контекст поисковый запрос и флаг суперпользователя.
    """
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        """
        Возвращает QuerySet пользователей, включая фильтрацию по поисковому запросу.

        Returns:
            QuerySet: Отфильтрованный QuerySet пользователей.
        """
        queryset = User.objects.all()  # Get all users, including inactive
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст поисковый запрос и флаг суперпользователя.

        Returns:
            dict: Словарь контекста.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список пользователей'
        context['q'] = self.request.GET.get('q', '')  # Pass the search query to the template
        context['is_superuser'] = self.request.user.is_superuser  # Передаем флаг суперпользователя в шаблон
        context['is_staff'] = self.request.user.is_staff
        return context


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, pk):
    """
    Представление для удаления пользователя (доступно только суперпользователям).

    Args:
        request: Объект запроса.
        pk (int):  ID пользователя, которого нужно удалить.

    Returns:
        HttpResponse:  Отображает страницу подтверждения удаления или перенаправляет на список пользователей.
    """
    user_to_delete = get_object_or_404(User, pk=pk)
    current_user = request.user

    if user_to_delete == current_user:
        messages.error(request, 'Вы не можете удалить самого себя!')
        return redirect('users:user_list')

    if request.method == 'POST':
        # Before deleting, remove the user from all groups:
        for group in user_to_delete.groups.all():
            user_to_delete.groups.remove(group)

        # Get all dogs owned by this user and set their owner to None
        dogs = Dog.objects.filter(owner=user_to_delete)
        for dog in dogs:
            dog.owner = None
            dog.save()

        # Physically delete the user:
        user_to_delete.delete()
        messages.success(request, f'Пользователь {user_to_delete.username} успешно удален.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user_to_delete})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_set_admin(request, pk):
    """
    Представление для изменения прав администратора пользователя (доступно только суперпользователям).

    Args:
        request: Объект запроса.
        pk (int): ID пользователя, для которого изменяются права.

    Returns:
        HttpResponse:  Отображает страницу подтверждения изменения прав или перенаправляет на список пользователей.
    """
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f'Права администратора для пользователя {user.username} изменены.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_set_admin.html', {'user': user})


# --- Helper Function (Password Generation) ---

def generate_random_password(length=12):
    """
    Генерирует случайный пароль заданной длины.

    Args:
        length (int):  Длина пароля.  По умолчанию 12.

    Returns:
        str: Сгенерированный пароль.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# --- User Detail View with Test Func (Superuser/Staff) ---
class UserDetailView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения детальной информации о пользователе.

    Наследует:
        LoginRequiredMixin:  Обеспечивает доступ только для авторизованных пользователей.
        TemplateView:  Базовый класс для представлений, отображающих шаблон.

    Атрибуты:
        template_name (str): Путь к шаблону для отображения информации о пользователе.

    Методы:
        test_func(self):  Определяет, имеет ли текущий пользователь доступ к представлению.
        get_context_data(**kwargs):  Получает контекст для отображения шаблона,
                                      включая информацию о просматриваемом пользователе и его собаках.
    """
    template_name = 'users/user_detail.html'

    def test_func(self):
        """
        Определяет, имеет ли текущий пользователь доступ к представлению.

        Returns:
            bool: True, если пользователь является суперпользователем или сотрудником,
                  иначе False.
        """
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """
        Получает контекст для отображения детальной информации о пользователе.

        Args:
            **kwargs:  Словарь дополнительных аргументов.

        Returns:
            dict: Словарь контекста, содержащий информацию о просматриваемом пользователе
                  и его собаках.
        """
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        user = get_object_or_404(User, pk=user_id)
        context['viewed_user'] = user
        context['dogs'] = Dog.objects.filter(owner=user)
        return context