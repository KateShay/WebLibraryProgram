import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_libsayan.settings')
django.setup()

from libsayan.models import Genre, Filial, Book, BookRequest, UserProfile, Event
from django.contrib.auth.models import User
from django.utils import timezone


def create_test_data():
    print("Начинаем заполнение базы данных тестовыми данными...")

    # ==================== 1. ЖАНРЫ (8 шт) ====================
    genres_data = [
        'Роман', 'Детектив', 'Фантастика', 'Поэзия',
        'История', 'Приключения', 'Научная литература', 'Фэнтези'
    ]

    genres = {}
    for g in genres_data:
        genre, created = Genre.objects.get_or_create(name=g)
        genres[g] = genre
        print(f"  Жанр: {g} - {'создан' if created else 'уже существует'}")

    # ==================== 2. ФИЛИАЛЫ (6 шт) ====================
    filials_data = [
        ('Центральная библиотека', 'ул. Ленина, 1, г. Саяногорск'),
        ('Детская библиотека', 'ул. Советская, 25, г. Саяногорск'),
        ('Библиотека "Радуга"', 'пр. Дружбы, 10, г. Саяногорск'),
        ('Библиотека "Родник"', 'ул. Лесная, 5, г. Саяногорск'),
        ('Библиотека "Майнская"', 'ул. Строителей, 15, п. Майна'),
        ('Библиотека для семьи', 'ул. Мира, 8, п. Черемушки'),
    ]

    filials = {}
    for name, address in filials_data:
        filial, created = Filial.objects.get_or_create(name=name, address=address)
        filials[name] = filial
        print(f"  Филиал: {name} - {'создан' if created else 'уже существует'}")

    # ==================== 3. ПОЛЬЗОВАТЕЛИ (6 шт) ====================
    users_data = [
        ('reader1', 'reader1@example.com', 'reader123', 'Читатель'),
        ('reader2', 'reader2@example.com', 'reader123', 'Читатель'),
        ('reader3', 'reader3@example.com', 'reader123', 'Читатель'),
        ('librarian', 'librarian@example.com', 'librarian123', 'librarian'),
        ('admin', 'admin@example.com', 'admin123', 'admin'),
    ]

    users = {}
    for username, email, password, role in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        if created:
            user.set_password(password)
            user.save()
        users[username] = user
        print(f"  Пользователь: {username} - {'создан' if created else 'уже существует'}")

        # Создаем профиль
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'phone': f'+7-999-123-{username[-2:] if username[-2].isdigit() else "01"}',
                'address': f'г. Саяногорск, ул. Примерная, д. {hash(username) % 100}'
            }
        )
        if not profile_created and profile.role != role:
            profile.role = role
            profile.save()

    # ==================== 4. КНИГИ (20 шт) ====================
    books_data = [
        # Название, Автор, Жанр, ISBN, Доступна
        ('Война и мир', 'Лев Толстой', 'Роман', '978-5-17-118890-0', True),
        ('Преступление и наказание', 'Фёдор Достоевский', 'Роман', '978-5-04-098634-5', True),
        ('Мастер и Маргарита', 'Михаил Булгаков', 'Роман', '978-5-699-78132-2', False),  # Недоступна
        ('Собачье сердце', 'Михаил Булгаков', 'Роман', '978-5-04-098635-2', True),
        ('Идиот', 'Фёдор Достоевский', 'Роман', '978-5-17-118891-7', True),
        ('Анна Каренина', 'Лев Толстой', 'Роман', '978-5-04-098636-9', True),
        ('Три товарища', 'Эрих Мария Ремарк', 'Роман', '978-5-17-118892-4', True),
        ('Убить пересмешника', 'Харпер Ли', 'Роман', '978-5-17-118893-1', True),
        ('1984', 'Джордж Оруэлл', 'Фантастика', '978-5-17-118894-8', True),
        ('Скотный двор', 'Джордж Оруэлл', 'Фантастика', '978-5-04-098637-6', True),
        ('О дивный новый мир', 'Олдос Хаксли', 'Фантастика', '978-5-17-118895-5', True),
        ('451 градус по Фаренгейту', 'Рэй Брэдбери', 'Фантастика', '978-5-04-098638-3', True),
        ('Гарри Поттер и философский камень', 'Джоан Роулинг', 'Фэнтези', '978-5-389-12345-6', True),
        ('Властелин колец', 'Джон Р.Р. Толкин', 'Фэнтези', '978-5-17-118896-2', False),  # Недоступна
        ('Пещера', 'Жозе Сарамаго', 'Роман', '978-5-04-098639-0', True),
        ('Сто лет одиночества', 'Габриэль Гарсиа Маркес', 'Роман', '978-5-17-118897-9', True),
        ('Евгений Онегин', 'Александр Пушкин', 'Поэзия', '978-5-04-098640-6', True),
        ('Мёртвые души', 'Николай Гоголь', 'Роман', '978-5-17-118898-6', True),
        ('Тихий Дон', 'Михаил Шолохов', 'Роман', '978-5-04-098641-3', True),
        ('Краткая история времени', 'Стивен Хокинг', 'Научная литература', '978-5-17-118899-3', True),
    ]

    books = {}
    for title, author, genre_name, isbn, available in books_data:
        genre = genres[genre_name]
        book, created = Book.objects.get_or_create(
            title=title,
            author=author,
            genre=genre,
            defaults={
                'isbn': isbn,
                'available': available
            }
        )
        books[title] = book
        print(f"  Книга: {title[:30]}... - {'создана' if created else 'уже существует'}")

    # ==================== 5. ЗАПРОСЫ КНИГ (10 шт) ====================
    requests_data = [
        # пользователь, книга, статус, дата запроса (дней назад)
        ('reader1', 'Война и мир', 'approved', 30),
        ('reader1', '1984', 'returned', 45),
        ('reader2', 'Мастер и Маргарита', 'pending', 2),
        ('reader2', 'Преступление и наказание', 'approved', 15),
        ('reader3', 'Властелин колец', 'pending', 1),
        ('reader1', 'Сто лет одиночества', 'rejected', 20),
        ('reader2', 'Гарри Поттер и философский камень', 'approved', 10),
        ('reader3', 'Три товарища', 'returned', 60),
        ('reader1', 'О дивный новый мир', 'pending', 3),
        ('reader2', 'Тихий Дон', 'approved', 5),
    ]

    for username, book_title, status, days_ago in requests_data:
        user = users[username]
        book = books[book_title]

        request_date = timezone.now() - timedelta(days=days_ago)

        book_request, created = BookRequest.objects.get_or_create(
            user=user,
            book=book,
            defaults={
                'status': status,
                'request_date': request_date
            }
        )

        if created:
            if status == 'approved':
                book_request.approved_date = request_date + timedelta(days=1)
            elif status == 'returned':
                book_request.approved_date = request_date + timedelta(days=1)
                book_request.return_date = request_date + timedelta(days=15)
            book_request.save()
            # Обновляем доступность книги
            if status in ['approved', 'pending']:
                book.available = False
                book.save()
            print(f"  Запрос: {username} -> {book_title[:20]}... ({status})")

    # ==================== 6. МЕРОПРИЯТИЯ (8 шт) ====================
    now = timezone.now()

    events_data = [
        ('Литературная гостиная "Поэзия серебряного века"',
         'Приглашаем всех любителей поэзии на встречу, посвящённую поэтам серебряного века. Будем читать стихи Блока, Ахматовой, Цветаевой.',
         now + timedelta(days=3), 'Центральная библиотека', 30),

        ('Мастер-класс "Как написать детектив"',
         'Встреча с известным писателем-детективщиком. Обсуждение жанра, секретов сюжета и создания интриги.',
         now + timedelta(days=7), 'Детская библиотека', 20),

        ('Книжный клуб "Читаем классику"',
         'Обсуждаем роман "Мастер и Маргарита". Приходите поделиться впечатлениями!',
         now + timedelta(days=14), 'Библиотека "Радуга"', 15),

        ('День открытых дверей',
         'Знакомство с библиотекой, экскурсия по фондам, презентация новых поступлений.',
         now + timedelta(days=5), 'Центральная библиотека', 50),

        ('Лекция "История книги"',
         'От глиняных табличек до электронных книг. Интересные факты из истории книгопечатания.',
         now + timedelta(days=10), 'Библиотека "Родник"', 25),

        ('Викторина "Знатоки литературы"',
         'Командная игра для школьников. Вопросы по русской и зарубежной классике.',
         now + timedelta(days=21), 'Детская библиотека', 40),

        ('Встреча с краеведом',
         'Презентация новой книги о истории города Саяногорска. Вход свободный.',
         now - timedelta(days=5), 'Библиотека "Майнская"', 0),  # Прошедшее

        ('Новогодний литературный вечер',
         'Праздничная программа, чтение стихов, конкурсы и чаепитие.',
         now + timedelta(days=30), 'Центральная библиотека', 35),
    ]

    events = []
    for title, description, event_date, filial_name, max_participants in events_data:
        filial = filials[filial_name]
        event, created = Event.objects.get_or_create(
            title=title,
            filial=filial,
            event_date=event_date,
            defaults={
                'description': description,
                'max_participants': max_participants
            }
        )
        events.append(event)
        print(f"  Мероприятие: {title[:30]}... - {'создано' if created else 'уже существует'}")

    # ==================== 7. УЧАСТНИКИ МЕРОПРИЯТИЙ ====================
    # Добавляем участников на мероприятия
    event_participants = [
        (events[0], ['reader1', 'reader2']),  # Литературная гостиная
        (events[1], ['reader1', 'reader3']),  # Мастер-класс по детективу
        (events[2], ['reader2', 'reader3']),  # Книжный клуб
        (events[3], ['reader1', 'reader2', 'reader3']),  # День открытых дверей
        (events[4], ['reader1']),  # Лекция по истории книги
        (events[6], ['reader2']),  # Встреча с краеведом (прошедшее)
    ]

    for event, usernames in event_participants:
        for username in usernames:
            user = users[username]
            event.participants.add(user)
        print(f"  Участники добавлены на: {event.title[:30]}...")

    # ==================== 8. СТАТИСТИКА ====================
    print("\n" + "=" * 50)
    print("СТАТИСТИКА ЗАГРУЗКИ ДАННЫХ:")
    print("=" * 50)
    print(f"  Жанры: {Genre.objects.count()}")
    print(f"  Филиалы: {Filial.objects.count()}")
    print(f"  Пользователи: {User.objects.count()}")
    print(f"  Профили пользователей: {UserProfile.objects.count()}")
    print(f"  Книги: {Book.objects.count()}")
    print(f"  Доступные книги: {Book.objects.filter(available=True).count()}")
    print(f"  Недоступные книги: {Book.objects.filter(available=False).count()}")
    print(f"  Запросы книг: {BookRequest.objects.count()}")
    print(f"  Мероприятия: {Event.objects.count()}")
    print(f"  Зарегистрированные участники мероприятий: {Event.participants.through.objects.count()}")

    # Статистика по статусам запросов
    print(f"\n  Статусы запросов:")
    print(f"    - Ожидают: {BookRequest.objects.filter(status='pending').count()}")
    print(f"    - Одобрены: {BookRequest.objects.filter(status='approved').count()}")
    print(f"    - Отклонены: {BookRequest.objects.filter(status='rejected').count()}")
    print(f"    - Возвращены: {BookRequest.objects.filter(status='returned').count()}")

    # Статистика по ролям пользователей
    print(f"\n  Роли пользователей:")
    for role, label in UserProfile.ROLE_CHOICES:
        count = UserProfile.objects.filter(role=role).count()
        print(f"    - {label}: {count}")

    print("\n" + "=" * 50)
    print("База данных успешно заполнена тестовыми данными!")
    print("=" * 50)


if __name__ == '__main__':
    create_test_data()