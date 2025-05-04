#my_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL-адреса для приложения 'users'
    path('users/', include('users.urls', namespace='users')),

    # URL-адреса для приложения 'dogs'
    path('', include('dogs.urls', namespace='dogs')),  # Включаем dogs.urls по корневому URL

    # URL-адреса для встроенной аутентификации Django (смена пароля, вход, выход и т.д.)
    path('accounts/', include('django.contrib.auth.urls')),
    
]

# Обслуживание медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


