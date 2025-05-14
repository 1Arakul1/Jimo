# dogs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Breed, Dog, Review
from .forms import DogForm, ReviewForm, ReviewUpdateForm, PedigreeFormSet  # Import PedigreeFormSet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, Http404
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q


class DogsListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка всех собак.

    Позволяет пользователям просматривать список собак, добавлять отзывы и фильтровать/искать собак.
    Требует авторизации.
    """
    model = Dog
    template_name = 'dogs/dogs_list.html'
    context_object_name = 'dogs'
    paginate_by = 6

    def get_queryset(self):
        """
        Возвращает отфильтрованный список объектов Dog.

        Фильтрует по запросу поиска, если он предоставлен.
        """
        queryset = Dog.objects.all().prefetch_related('reviews__user')

        # ПОИСК
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(owner__username__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Включает заголовок, форму отзыва и запрос поиска.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список всех собак'
        context['review_form'] = ReviewForm()
        context['search_query'] = self.request.GET.get('q', '')  # Передаем запрос в шаблон
        return context

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы для добавления отзывов к собакам.

        Сохраняет новый отзыв, связанный с собакой и пользователем.
        """
        dog_id = request.POST.get('dog_id')
        dog = get_object_or_404(Dog, pk=dog_id)
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.dog = dog
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect(reverse('dogs:dogs_list') + f'?page={request.GET.get("page", 1)}&q={self.request.GET.get("q", "")}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            context = self.get_context_data()
            context['review_form'] = form
            return self.render_to_response(context)


class AddDogToProfileView(LoginRequiredMixin, View):
    """
    Представление для добавления собаки в профиль пользователя.

    Позволяет авторизованным пользователям добавить собаку в свой профиль.
    """
    def post(self, request, dog_id):
        """
        Обрабатывает POST-запросы для добавления собаки.

        Проверяет, принадлежит ли собака уже другому пользователю.
        Добавляет собаку текущему пользователю, если это возможно.
        """
        dog = get_object_or_404(Dog, pk=dog_id)

        if dog.owner is not None:
            messages.error(request, f"Собака '{dog.name}' уже принадлежит {dog.owner.username}.")
        else:
            dog.owner = request.user
            dog.save()
            messages.success(request, f"Собака '{dog.name}' успешно добавлена в ваш профиль.")

        return redirect(reverse('dogs:dogs_list') + f'?q={self.request.GET.get("q", "")}')  # Передаем параметр поиска


class RemoveDogFromProfileView(LoginRequiredMixin, View):
    """
    Представление для удаления собаки из профиля пользователя.

    Позволяет авторизованным пользователям удалить собаку из своего профиля.
    """
    def post(self, request, dog_id):
        """
        Обрабатывает POST-запросы для удаления собаки.

        Удаляет собаку из профиля текущего пользователя.
        Возвращает JSON-ответ с сообщением об успехе или ошибке.
        """
        try:
            dog = get_object_or_404(Dog, pk=dog_id, owner=request.user)
            dog.owner = None
            dog.save()
            return JsonResponse({'message': f'Собака "{dog.name}" успешно удалена из профиля.'})
        except Http404:
            return JsonResponse({'message': 'У вас нет прав на удаление этой собаки.'}, status=403)
        except Exception as e:
            return JsonResponse({'message': f'Произошла ошибка: {str(e)}'}, status=500)


class IndexView(LoginRequiredMixin, TemplateView):
    """
    Представление для главной страницы.

    Отображает главную страницу приложения.
    Требует авторизации.
    """
    template_name = 'dogs/index.html'
    extra_context = {'title': 'Главная страница'}


class BreedsView(LoginRequiredMixin, ListView):  # Изменено на ListView
    """
    Представление для отображения списка пород собак.

    Отображает список пород с возможностью пагинации и поиска.
    Требует авторизации.
    """
    model = Breed
    template_name = 'dogs/breeds.html'
    context_object_name = 'breeds_data'  # Используем другое имя для удобства
    paginate_by = 6  # Добавлена пагинация

    def get_queryset(self):
        """
        Возвращает отфильтрованный список пород.

        Фильтрует по запросу поиска, если он предоставлен.
        """
        breeds = Breed.objects.prefetch_related('dogs')

        #  ПОИСК
        search_query = self.request.GET.get('q')
        if search_query:
            breeds = breeds.filter(name__icontains=search_query)

        breeds_data = []  # Формируем данные для шаблона
        for breed in breeds:
            dogs = breed.dogs.order_by('?')[:3]
            breeds_data.append({'breed': breed, 'dogs': dogs})

        return breeds_data  # Возвращаем список словарей

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Включает заголовок, запрос поиска и объект пагинации.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Породы собак'
        context['search_query'] = self.request.GET.get('q', '')  # Передаем запрос в шаблон

        # Пагинация
        paginator = Paginator(self.object_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)

        context['breeds_data'] = page_obj  # Передаем объект страницы
        return context


class DogCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой собаки.

    Позволяет авторизованным пользователям создавать новых собак.
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_create.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def get_context_data(self, **kwargs):
        """
        Добавляет формы для родословной в контекст.

        Отображает пустые формы для родословной, если это POST-запрос.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST)
        else:
            context['pedigree_formset'] = PedigreeFormSet()
        return context

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы создания собаки.

        Сохраняет информацию о собаке и связанные данные родословной.
        """
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']
        if pedigree_formset.is_valid():
            try:
                form.instance.clean()
            except ValidationError as e:
                form.add_error('birth_date', e)
                return self.form_invalid(form)

            # form.instance.owner = self.request.user  # Убрали эту строку
            self.object = form.save()  # Сохраняем Dog instance, чтобы использовать его для pedigree_formset
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            messages.success(self.request, f"Собака '{form.instance.name}' успешно добавлена!")
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме родословной.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверную отправку формы создания собаки.

        Отображает сообщения об ошибках.
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного создания собаки.

        Включает параметр поиска, если он был передан.
        """
        return reverse('dogs:dogs_list') + f'?q={self.request.GET.get("q", "")}'  # Передаем параметр поиска


class DogUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования информации о собаке.

    Позволяет авторизованным пользователям редактировать информацию о своих собаках.
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_update.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """
        Добавляет формы для родословной в контекст.

        Передает существующие данные родословной в форму, если это POST-запрос.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.get_object())
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.get_object())
        return context

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы редактирования собаки.

        Сохраняет обновленную информацию о собаке и связанные данные родословной.
        """
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']
        if pedigree_formset.is_valid():
            try:
                form.instance.clean()
            except ValidationError as e:
                form.add_error('birth_date', e)
                return self.form_invalid(form)

            form.instance.owner = self.request.user
            self.object = form.save()  # Сохраняем Dog instance, чтобы использовать его для pedigree_formset
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            messages.success(self.request, f"Информация о собаке '{form.instance.name}' успешно обновлена!")
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме родословной.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверную отправку формы редактирования собаки.

        Отображает сообщения об ошибках.
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного редактирования собаки.

        Включает параметр поиска, если он был передан.
        """
        return reverse('dogs:dogs_list') + f'?q={self.request.GET.get("q", "")}'  # Передаем параметр поиска


class DogDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления собаки.

    Позволяет авторизованным пользователям удалять информацию о своих собаках.
    """
    model = Dog
    template_name = 'dogs/dog_confirm_delete.html'

    def get_object(self, queryset=None):
        """
        Возвращает объект собаки, который нужно удалить.

        Получает объект по slug.
        """
        return get_object_or_404(Dog, slug=self.kwargs['slug'])

    def delete(self, request, *args, **kwargs):
        """
        Обрабатывает удаление объекта.

        Отображает сообщение об успехе.
        """
        dog = self.get_object()
        messages.success(request, f"Собака '{dog.name}' успешно удалена.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления собаки.

        Включает параметр поиска, если он был передан.
        """
        return reverse('dogs:dogs_list') + f'?q={self.request.GET.get("q", "")}'  # Передаем параметр поиска


class DogReadView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения детальной информации о собаке.

    Позволяет пользователям просматривать подробную информацию о конкретной собаке.
    """
    model = Dog
    template_name = 'dogs/dog_read.html'
    context_object_name = 'dog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы.

        Увеличивает счетчик просмотров, если просмотр осуществляется не владельцем.
        Отправляет уведомление владельцу, если количество просмотров кратно 100.
        """
        self.object = self.get_object()
        # Увеличиваем счетчик, если пользователь не владелец
        if self.object.owner != request.user:
            self.object.views_count += 1
            self.object.save()

            # Проверяем кратность 100 и отправляем письмо
            if self.object.views_count % 100 == 0 and self.object.owner:
                self.send_views_notification_email(self.object)  # Вызов функции отправки email

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Включает заголовок, информацию о владельце и родословной.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Информация о собаке'
        context['is_owner'] = self.object.owner == self.request.user
        try:
            # Пытаемся получить родословную для данной собаки
            context['pedigree'] = self.object.pedigrees.get()  # Используем related_name 'pedigrees'
        except Pedigree.DoesNotExist:
            # Если родословной нет, передаем None
            context['pedigree'] = None
        return context

    def send_views_notification_email(self, dog):
        """
        Отправляет уведомление владельцу о количестве просмотров.

        Использует django.core.mail.send_mail для отправки email.
        """
        subject = f'Вашу собаку {dog.name} просмотрели {dog.views_count} раз!'
        message = f'Поздравляем! Карточку вашей собаки {dog.name} просмотрели {dog.views_count} раз. Спасибо за использование нашего сервиса!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [dog.owner.email]  # Отправляем владельцу
        send_mail(subject, message, from_email, recipient_list)


class BreedDetailView(LoginRequiredMixin, DetailView):  # Добавлено
    """
    Представление для отображения детальной информации о породе.

    Позволяет пользователям просматривать подробную информацию о конкретной породе.
    Требует авторизации.
    """
    model = Breed
    template_name = 'dogs/breed_detail.html'
    context_object_name = 'breed'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


# Добавьте или обновите ProfileView
class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения профиля пользователя.

    Позволяет пользователям просматривать свой профиль, включая список своих собак.
    Требует авторизации.
    """
    template_name = 'profile.html'  # Замените на имя вашего шаблона профиля

    def get_context_data(self, **kwargs):
        """
        Добавляет информацию о собаках пользователя в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['dogs'] = Dog.objects.filter(owner=user)  # Получаем собак из БД
        context['is_superuser'] = user.is_superuser
        return context


# ----- Новые классы для редактирования и удаления отзывов -----

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования отзыва.

    Позволяет пользователям редактировать свои отзывы.
    Требует авторизации.
    """
    model = Review
    form_class = ReviewUpdateForm
    template_name = 'dogs/review_update.html'  # Создайте этот шаблон
    # Успешный редирект обратно на список собак, сохраняя номер страницы
    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного обновления отзыва.
        """
        return reverse('dogs:dogs_list') + f'?page={self.request.GET.get("page", 1)}&q={self.request.GET.get("q", "")}'

    def get_object(self, queryset=None):
        """
        Возвращает объект отзыва для редактирования.

        Проверяет права доступа (только для администраторов, модераторов или владельцев отзыва).
        """
        review = super().get_object(queryset=queryset)
        # Проверка прав: админ, модератор или владелец отзыва
        if not (self.request.user.is_staff or self.request.user == review.user):
            raise Http404("У вас нет прав на редактирование этого отзыва.")
        return review

    def form_valid(self, form):
        """
        Обрабатывает успешное обновление отзыва.

        Обновляет дату последнего изменения.
        Отображает сообщение об успехе.
        """
        form.instance.updated_at = timezone.now()  # Обновляем время изменения
        messages.success(self.request, "Отзыв успешно обновлен!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает неверные данные в форме редактирования отзыва.

        Отображает сообщение об ошибке.
        """
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления отзыва.

    Позволяет пользователям удалять свои отзывы.
    Требует авторизации.
    """
    model = Review
    template_name = 'dogs/review_confirm_delete.html'  # Создайте этот шаблон

    # Успешный редирект обратно на список собак, сохраняя номер страницы
    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления отзыва.
        """
        return reverse('dogs:dogs_list') + f'?page={self.request.GET.get("page", 1)}&q={self.request.GET.get("q", "")}'

    def get_object(self, queryset=None):
        """
        Возвращает объект отзыва для удаления.

        Проверяет права доступа (только для администраторов, модераторов или владельцев отзыва).
        """
        review = super().get_object(queryset=queryset)
        # Проверка прав: админ, модератор или владелец отзыва
        if not (self.request.user.is_staff or self.request.user == review.user):
            raise Http404("У вас нет прав на удаление этого отзыва.")
        return review

    def delete(self, request, *args, **kwargs):
        """
        Обрабатывает удаление отзыва.

        Отображает сообщение об успехе.
        """
        messages.success(request, "Отзыв успешно удален.")
        return super().delete(request, *args, **kwargs)