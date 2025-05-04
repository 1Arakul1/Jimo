from django.shortcuts import render, redirect, get_object_or_404
from .models import Breed, Dog, Review  # Import Review
from .forms import DogForm, ReviewForm, ReviewUpdateForm  # Import ReviewForm и ReviewUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, Http404
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.mail import send_mail  # Импорт для отправки email
from django.conf import settings  # импорт настроек
from django.contrib.auth.decorators import login_required  # нужен для form_valid
from django.utils.decorators import method_decorator
from django.utils import timezone  # Для работы со временем
from django.contrib.auth.models import User  # Import User model

class DogsListView(LoginRequiredMixin, ListView):
    model = Dog
    template_name = 'dogs/dogs_list.html'
    context_object_name = 'dogs'
    paginate_by = 6

    def get_queryset(self):
        return Dog.objects.all().prefetch_related('reviews__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список всех собак'
        context['review_form'] = ReviewForm()  # Добавляем форму отзыва
        return context

    def post(self, request, *args, **kwargs):
        dog_id = request.POST.get('dog_id')
        dog = get_object_or_404(Dog, pk=dog_id)
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.dog = dog
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect(reverse('dogs:dogs_list') + f'?page={request.GET.get("page", 1)}')  # Redirect to the same page
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            context = self.get_context_data()
            context['review_form'] = form
            return self.render_to_response(context)

class AddDogToProfileView(LoginRequiredMixin, View):
    def post(self, request, dog_id):
        dog = get_object_or_404(Dog, pk=dog_id)

        if dog.owner is not None:
            messages.error(request, f"Собака '{dog.name}' уже принадлежит {dog.owner.username}.")
        else:
            dog.owner = request.user
            dog.save()
            messages.success(request, f"Собака '{dog.name}' успешно добавлена в ваш профиль.")

        return redirect(reverse('dogs:dogs_list'))  # Перенаправляем на dogs_list

class RemoveDogFromProfileView(LoginRequiredMixin, View):
    def post(self, request, dog_id):
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
    template_name = 'dogs/index.html'
    extra_context = {'title': 'Главная страница'}


class BreedsView(LoginRequiredMixin, TemplateView):
    template_name = 'dogs/breeds.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = 'Породы собак'
        breeds = Breed.objects.prefetch_related('dogs').all()
        breeds_data = []
        for breed in breeds:
            dogs = breed.dogs.order_by('?')[:3]
            breeds_data.append({'breed': breed, 'dogs': dogs})
        context['title'] = title
        context['breeds_data'] = breeds_data
        return context

class DogCreateView(LoginRequiredMixin, CreateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_create.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def form_valid(self, form):
        try:
            form.instance.clean()
        except ValidationError as e:
            form.add_error('birth_date', e)
            return self.form_invalid(form)

        form.instance.owner = self.request.user
        messages.success(self.request, f"Собака '{form.instance.name}' успешно добавлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)


class DogUpdateView(LoginRequiredMixin, UpdateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_update.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def get_object(self, queryset=None):
        dog = super().get_object(queryset=queryset)
        if dog.owner != self.request.user and not self.request.user.is_staff:
            raise Http404("У вас нет прав на редактирование этой собаки.")
        return dog

    def get_form_class(self):  # ИЗМЕНЕНО: Вместо get_form(), используем get_form_class()
        """
        Возвращает класс формы, который будет использоваться.
        Ограничивает поля формы в зависимости от прав пользователя.
        """
        if self.request.user.is_staff:
            # Администратору видны все поля
            return self.form_class  # Возвращаем исходный класс формы
        else:
            # Обычным пользователям не видны поля
            class RestrictedDogForm(self.form_class): #Создаем новую форму, наследуясь от исходной
                class Meta(self.form_class.Meta): #Переиспользуем метаданные
                    fields = ['name', 'breed', 'age', 'description', 'image', 'birth_date']  # Только эти поля
            return RestrictedDogForm #Возвращаем класс ограниченной формы

    @method_decorator(login_required)
    def form_valid(self, form):
        messages.success(self.request, f"Информация о собаке '{form.instance.name}' успешно обновлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)


class DogDeleteView(LoginRequiredMixin, DeleteView):
    model = Dog
    template_name = 'dogs/dog_confirm_delete.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def get_object(self, queryset=None):
        dog = super().get_object(queryset=queryset)
        if dog.owner != self.request.user:
            raise Http404("У вас нет прав на удаление этой собаки.")
        return dog

    def delete(self, request, *args, **kwargs):
        dog = self.get_object()
        messages.success(request, f"Собака '{dog.name}' успешно удалена.")
        return super().delete(request, *args, **kwargs)


class DogReadView(LoginRequiredMixin, DetailView):
    model = Dog
    template_name = 'dogs/dog_read.html'
    context_object_name = 'dog'

    def get(self, request, *args, **kwargs):
        """
        Увеличивает счетчик просмотров при каждом запросе.
        """
        self.object = self.get_object()
        # Увеличиваем счетчик, если пользователь не владелец
        if self.object.owner != request.user:
            self.object.views_count += 1
            self.object.save()

            # Проверяем кратность 100 и отправляем письмо
            if self.object.views_count % 100 == 0 and self.object.owner:
                self.send_views_notification_email(self.object) # Вызов функции отправки email

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Информация о собаке'
        context['is_owner'] = self.object.owner == self.request.user
        return context

    def send_views_notification_email(self, dog):
        """
        Отправляет уведомление владельцу о количестве просмотров.
        """
        subject = f'Вашу собаку {dog.name} просмотрели {dog.views_count} раз!'
        message = f'Поздравляем! Карточку вашей собаки {dog.name} просмотрели {dog.views_count} раз. Спасибо за использование нашего сервиса!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [dog.owner.email]  # Отправляем владельцу
        send_mail(subject, message, from_email, recipient_list)

# Добавьте или обновите ProfileView
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'  # Замените на имя вашего шаблона профиля

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['dogs'] = Dog.objects.filter(owner=user)  # Получаем собак из БД
        context['is_superuser'] = user.is_superuser
        return context


# ----- Новые классы для редактирования и удаления отзывов -----

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewUpdateForm
    template_name = 'dogs/review_update.html'  # Создайте этот шаблон
    # Успешный редирект обратно на список собак, сохраняя номер страницы
    def get_success_url(self):
        return reverse('dogs:dogs_list') + f'?page={self.request.GET.get("page", 1)}'

    def get_object(self, queryset=None):
        review = super().get_object(queryset=queryset)
        # Проверка прав: админ, модератор или владелец отзыва
        if not (self.request.user.is_staff or self.request.user == review.user):
            raise Http404("У вас нет прав на редактирование этого отзыва.")
        return review

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()  # Обновляем время изменения
        messages.success(self.request, "Отзыв успешно обновлен!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'dogs/review_confirm_delete.html'  # Создайте этот шаблон

    # Успешный редирект обратно на список собак, сохраняя номер страницы
    def get_success_url(self):
        return reverse('dogs:dogs_list') + f'?page={self.request.GET.get("page", 1)}'

    def get_object(self, queryset=None):
        review = super().get_object(queryset=queryset)
        # Проверка прав: админ, модератор или владелец отзыва
        if not (self.request.user.is_staff or self.request.user == review.user):
            raise Http404("У вас нет прав на удаление этого отзыва.")
        return review

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Отзыв успешно удален.")
        return super().delete(request, *args, **kwargs)