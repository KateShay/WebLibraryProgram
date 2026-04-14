from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название жанра")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.CharField(max_length=200, verbose_name="Автор")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")
    isbn = models.CharField(max_length=20, verbose_name="ISBN", blank=True)
    available = models.BooleanField(default=True, verbose_name="Доступна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('returned', 'Возвращено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Читатель")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата запроса")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата одобрения")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата возврата")

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    class Meta:
        verbose_name = "Запрос книги"
        verbose_name_plural = "Запросы книг"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('guest','Гость'),
        ('reader', 'Читатель'),
        ('librarian', 'Библиотекарь'),
        ('admin', 'Администратор')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest', verbose_name="Роль")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class Filial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.CharField(max_length=200, verbose_name="Адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"
