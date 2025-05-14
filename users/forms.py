# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User  # Важно: импортируем вашу кастомную модель!

class LoginForm(AuthenticationForm):
    """
    Форма для входа пользователя.

    Наследует:
        AuthenticationForm:  Стандартная форма аутентификации Django.

    Поля:
        username:  Имя пользователя (TextInput).
        password:  Пароль (PasswordInput).

    Виджеты:
        TextInput:  Виджет для ввода имени пользователя.
        PasswordInput:  Виджет для ввода пароля.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')

class RegisterForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.

    Наследует:
        UserCreationForm:  Стандартная форма создания пользователя Django.

    Поля:
        email:  Электронная почта (EmailField).

    Методы:
        clean_username():  Проверяет, что имя пользователя не занято.
        save(commit=True):  Сохраняет пользователя, включая email.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')

    class Meta:
        model = User
        fields = ("username", "email")  # Указываем поля, которые будут отображаться в форме

    def clean_username(self):
        """
        Проверяет, что имя пользователя еще не занято.

        Raises:
            forms.ValidationError:  Если имя пользователя уже занято.

        Returns:
            str:  Очищенное имя пользователя.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

    def save(self, commit=True):
        """
        Сохраняет пользователя.

        Args:
            commit (bool):  Флаг, указывающий, нужно ли сохранять объект в базу данных.

        Returns:
            User:  Созданный пользователь.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Сохраняем email
        if commit:
            user.save()
        return user

class EditProfileForm(UserChangeForm):
    """
    Форма для редактирования профиля пользователя.

    Наследует:
        UserChangeForm:  Стандартная форма изменения пользователя Django.

    Поля:
        email:  Электронная почта (EmailField).

    Методы:
        __init__(*args, **kwargs):  Инициализация формы, убирает help_text для полей.
    """
    password = None  # Убираем поле password из формы

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.

        Убирает help_text для полей.
        """
        super().__init__(*args, **kwargs)
        # Убираем help_text для полей (необязательно)
        self.fields['email'].help_text = None

class PasswordResetRequestForm(forms.Form):
    """
    Форма для запроса сброса пароля.

    Поля:
        email:  Электронная почта (EmailField).

    Виджеты:
        EmailInput:  Виджет для ввода электронной почты.
    """
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control'}))