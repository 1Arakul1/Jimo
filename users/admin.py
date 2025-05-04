from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Product  #  Импортируем Product

User = get_user_model()

admin.site.register(Product)  # Регистрируем Product в админке