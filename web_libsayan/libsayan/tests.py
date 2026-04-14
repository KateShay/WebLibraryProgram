from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Book, BookRequest, Genre, UserProfile


class SimpleTest(TestCase):
    """Тесты библиотечной системы"""

    def setUp(self):
        """Создание необходимых данных перед каждым тестом"""
        self.genre = Genre.objects.create(name="Тестовый жанр")

        self.user = User.objects.create_user(
            username='reader',
            password='pass'
        )
        UserProfile.objects.create(
            user=self.user,
            role='reader'
        )

    def test_simple(self):
        """Простой тест для проверки работы"""
        self.assertEqual(1, 1)

    def test_book_soft_delete(self):
        """Тест мягкого удаления книги"""
        # Создаём книгу
        book = Book.objects.create(
            title="Тест",
            author="Автор",
            genre=self.genre
        )

        # Проверяем, что delete_date пуст
        self.assertIsNone(book.delete_date)

        # Проверяем, что книга находится в "активных" (не удалённых)
        active_books = Book.objects.filter(delete_date__isnull=True)
        self.assertIn(book, active_books)

        # Мягкое удаление
        book.soft_delete()

        # Проверяем, что delete_date заполнен
        self.assertIsNotNone(book.delete_date)

        # Проверяем, что книга НЕ в списке активных (не удалённых)
        active_books = Book.objects.filter(delete_date__isnull=True)
        self.assertNotIn(book, active_books)

        # Восстановление
        book.restore()

        # Проверяем, что delete_date снова пуст
        self.assertIsNone(book.delete_date)

        # Проверяем, что книга снова в списке активных
        active_books = Book.objects.filter(delete_date__isnull=True)
        self.assertIn(book, active_books)

    def test_request_book(self):
        """Тест запроса книги"""
        self.client.login(username='reader', password='pass')

        book = Book.objects.create(
            title="Книга",
            author="Автор",
            genre=self.genre,
            available=True
        )

        # Проверяем, что книга доступна
        self.assertTrue(book.available)

        # Отправляем запрос
        response = self.client.post(reverse('request_book', args=[book.id]))

        # Проверяем редирект (302)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что книга стала НЕдоступной
        book.refresh_from_db()
        self.assertFalse(book.available)

        # Проверяем, что создался ровно 1 запрос
        self.assertEqual(BookRequest.objects.filter(book=book).count(), 1)