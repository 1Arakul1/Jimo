# users/urls.py
from django.urls import path
from . import views
from .views import (
    UserProfileView,
    EditProfileView,
    LogoutView,
    RegisterView,
    UserLoginView,
    WelcomeView,
    LogoutSuccessView,
    ChangePasswordView,
    PasswordResetRequestView,
    UserListView,
    user_delete,
    user_set_admin,
    UserDetailView
)

app_name = 'users'

urlpatterns = [
    # --- Authentication URLs ---
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout_success/', LogoutSuccessView.as_view(), name='logout_success'),
    path('welcome/', WelcomeView.as_view(), name='welcome'),

    # --- User Profile URLs ---
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/change_password/', ChangePasswordView.as_view(), name='change_password'),

    # --- Password Reset URLs ---
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),

    # --- User Management URLs (Superuser Only) ---
    path('list/', UserListView.as_view(), name='user_list'),
    path('delete/<int:pk>/', views.user_delete, name='user_delete'),
    path('set_admin/<int:pk>/', views.user_set_admin, name='user_set_admin'),
    path('detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),  # Добавляем URL для просмотра деталей
]