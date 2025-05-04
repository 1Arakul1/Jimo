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
class UserDetailView(LoginRequiredMixin, TemplateView):  # Убрали UserPassesTestMixin
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        context['viewed_user'] = get_object_or_404(User, pk=user_id)
        context['dogs'] = Dog.objects.filter(owner=context['viewed_user'])
        return context

# --- User Authentication Views ---

class UserLoginView(FormView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
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
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return self.render_to_response(self.get_context_data(form=form))


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'users/register.html'

    def form_valid(self, form):
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
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(RedirectView):
    url = reverse_lazy('users:logout_success')

    def get(self, request, *args, **kwargs):
        django_logout(request)
        return super().get(request, *args, **kwargs)


class LogoutSuccessView(TemplateView):
    template_name = 'users/logout_success.html'

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WelcomeView(LoginRequiredMixin, TemplateView):
    template_name = 'users/welcome.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# --- User Profile Views ---

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        context['user'] = self.request.user
        context['dogs'] = Dog.objects.filter(owner=self.request.user)
        context['is_superuser'] = self.request.user.is_superuser
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:user_profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:user_profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)


# --- Password Reset Views ---

class PasswordResetRequestView(FormView):
    form_class = PasswordResetRequestForm
    template_name = 'users/password_reset_request.html'
    success_url = reverse_lazy('users:user_login')  # Redirect to login after reset

    def form_valid(self, form):
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
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return self.render_to_response(self.get_context_data(form=form))


# class PasswordResetConfirmView(TemplateView):  # Removed PasswordResetConfirmView
#     template_name = 'users/password_reset_confirm.html'
#     def get(self, request, token):
#         try:
#             user = User.objects.get(password_reset_token=token)
#         except User.DoesNotExist:
#             messages.error(request, "Неверный токен сброса пароля.")
#             return redirect('users:password_reset_request')
#
#         context = {'token': token, 'user': user}
#         return self.render_to_response(context)
#
#     def post(self, request, token):
#         try:
#             user = User.objects.get(password_reset_token=token)
#         except User.DoesNotExist:
#             messages.error(request, "Неверный токен сброса пароля.")
#             return redirect('users:password_reset_request')
#         new_password1 = request.POST.get('new_password1')
#         new_password2 = request.POST.get('new_password2')
#
#         if new_password1 == new_password2:
#             user.set_password(new_password1)
#             user.password_reset_token = None # Clear the token
#             user.save()
#             messages.success(request, "Пароль успешно изменен. Теперь вы можете войти с новым паролем.")
#             return redirect('users:user_login')
#         else:
#             messages.error(request, "Пароли не совпадают.")
#             context = {'token': token}
#             return self.render_to_response(context)


# --- User Management Views (Superuser Only) ---

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.all()  # Get all users, including inactive
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список пользователей'
        context['q'] = self.request.GET.get('q', '')  # Pass the search query to the template
        context['is_superuser'] = self.request.user.is_superuser  # Передаем флаг суперпользователя в шаблон
        context['is_staff'] = self.request.user.is_staff
        return context


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, pk):
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
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f'Права администратора для пользователя {user.username} изменены.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_set_admin.html', {'user': user})


# --- Helper Function (Password Generation) ---

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# --- User Detail View ---
class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        user = get_object_or_404(User, pk=user_id)
        context['viewed_user'] = user
        context['dogs'] = Dog.objects.filter(owner=user)
        return context