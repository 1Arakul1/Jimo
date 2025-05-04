# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User  # Важно: импортируем вашу кастомную модель!

class LoginForm(AuthenticationForm):
    """
    Форма для входа пользователя.
    Использует AuthenticationForm из django.contrib.auth.forms для обработки аутентификации.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')

class RegisterForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    Наследуется от UserCreationForm и добавляет поле email.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')

    class Meta:
        model = User
        fields = ("username", "email")  # Указываем поля, которые будут отображаться в форме

    def clean_username(self):
        """
        Проверяет, что имя пользователя еще не занято.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

    def save(self, commit=True):
        """
        Сохраняет пользователя.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Сохраняем email
        if commit:
            user.save()
        return user

class EditProfileForm(UserChangeForm):
    """
    Форма для редактирования профиля пользователя.
    Наследуется от UserChangeForm и позволяет изменять email. Удалены first_name и last_name.
    """
    password = None  # Убираем поле password из формы

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем help_text для полей (необязательно)
        self.fields['email'].help_text = None

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control'}))