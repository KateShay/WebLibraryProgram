import os
import io
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Book, BookRequest, Event, Genre, Filial, UserProfile
import matplotlib.pyplot as plt


def delete_old_image(book_instance, new_image):
    try:
        if book_instance.pk:
            old_book = Book.objects.get(pk=book_instance.pk)
            if old_book.image and old_book.image != new_image:
                if os.path.isfile(old_book.image.path):
                    os.remove(old_book.image.path)
    except Exception:
        pass


def is_reader(user):
    return hasattr(user, 'userprofile') and user.userprofile.role in ['reader', 'librarian', 'admin']


def is_librarian(user):
    return hasattr(user, 'userprofile') and user.userprofile.role in ['librarian', 'admin']


def index(request):
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now(), delete_date__isnull=True).order_by(
        'event_date')[:6]
    return render(request, 'index.html', {'upcoming_events': upcoming_events})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='reader')
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def book_list(request):
    books = Book.objects.filter(delete_date__isnull=True)

    query = request.GET.get('q', '')
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))

    genre_id = request.GET.get('genre')
    if genre_id:
        books = books.filter(genre_id=genre_id)

    sort = request.GET.get('sort', 'title')
    if sort == 'author':
        books = books.order_by('author')
    elif sort == 'genre':
        books = books.order_by('genre__name')
    else:
        books = books.order_by('title')

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Genre.objects.filter(delete_date__isnull=True)

    return render(request, 'book_list.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'selected_genre': genre_id,
        'sort': sort
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id, delete_date__isnull=True)
    return render(request, 'book_detail.html', {'book': book})


@login_required
@user_passes_test(is_reader)
def request_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, delete_date__isnull=True)
    if not book.available:
        messages.error(request, "Книга недоступна.")
        return redirect('book_detail', book_id=book.id)

    if request.method == 'POST':
        BookRequest.objects.create(user=request.user, book=book, status='pending')
        book.available = False
        book.save()
        messages.success(request, "Запрос отправлен. Ожидайте одобрения.")
        return redirect('my_requests')

    return render(request, 'request_book.html', {'book': book})


@login_required
def my_requests(request):
    requests_list = BookRequest.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'my_requests.html', {'requests': requests_list})


@login_required
@user_passes_test(is_librarian)
def manage_requests(request):
    pending_requests = BookRequest.objects.filter(status='pending').order_by('request_date')

    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')
        book_req = get_object_or_404(BookRequest, id=req_id)

        if action == 'approve':
            book_req.status = 'approved'
            book_req.approved_date = timezone.now()
            book_req.save()
            messages.success(request, f"Запрос одобрен.")
        elif action == 'reject':
            book_req.status = 'rejected'
            book_req.save()
            book = book_req.book
            book.available = True
            book.save()
            messages.success(request, f"Запрос отклонён.")
        return redirect('manage_requests')

    return render(request, 'manage_requests.html', {'requests': pending_requests})


@login_required
@user_passes_test(is_librarian)
def return_book(request, request_id):
    book_req = get_object_or_404(BookRequest, id=request_id, status='approved')
    book_req.status = 'returned'
    book_req.return_date = timezone.now()
    book_req.save()
    book = book_req.book
    book.available = True
    book.save()
    messages.success(request, f"Книга возвращена.")
    return redirect('manage_requests')


@login_required
@user_passes_test(is_librarian)
def book_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        genre_id = request.POST.get('genre')
        isbn = request.POST.get('isbn', '')
        available = request.POST.get('available') == 'on'
        image = request.FILES.get('image')

        if not title or not author or not genre_id:
            messages.error(request, "Заполните обязательные поля.")
        else:
            book = Book(
                title=title,
                author=author,
                genre_id=genre_id,
                isbn=isbn,
                available=available,
                image=image
            )
            book.save()
            messages.success(request, "Книга добавлена.")
            return redirect('book_list')

    genres = Genre.objects.filter(delete_date__isnull=True)
    return render(request, 'book_form.html', {'genres': genres, 'title': 'Добавление книги'})


@login_required
@user_passes_test(is_librarian)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.genre_id = request.POST.get('genre')
        book.isbn = request.POST.get('isbn', '')
        book.available = request.POST.get('available') == 'on'

        if 'image' in request.FILES:
            delete_old_image(book, request.FILES['image'])
            book.image = request.FILES['image']

        book.save()
        messages.success(request, "Книга обновлена.")
        return redirect('book_list')

    genres = Genre.objects.filter(delete_date__isnull=True)
    return render(request, 'book_form.html', {
        'book': book,
        'genres': genres,
        'title': 'Редактирование книги',
        'book_id': book.pk
    })


@login_required
@user_passes_test(is_librarian)
def book_soft_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    try:
        book.soft_delete()
        messages.success(request, f'Книга "{book.title}" перемещена в корзину.')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
    return redirect('book_list')


def event_list(request):
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now(), delete_date__isnull=True).order_by(
        'event_date')
    past_events = Event.objects.filter(event_date__lt=timezone.now(), delete_date__isnull=True).order_by('-event_date')
    return render(request, 'event_list.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, delete_date__isnull=True)
    user_registered = False
    if request.user.is_authenticated:
        user_registered = event.participants.filter(id=request.user.id).exists()
    return render(request, 'event_detail.html', {
        'event': event,
        'user_registered': user_registered,
        'now': timezone.now()
    })


@login_required
@user_passes_test(is_reader)
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, delete_date__isnull=True)

    if event.event_date < timezone.now():
        messages.error(request, "Нельзя записаться на прошедшее мероприятие.")
        return redirect('event_detail', event_id=event.id)

    if event.is_full():
        messages.error(request, "Мероприятие уже заполнено.")
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        event.participants.add(request.user)
        messages.success(request, f"Вы записаны на мероприятие '{event.title}'.")
        return redirect('event_detail', event_id=event.id)

    return render(request, 'register_event.html', {'event': event})


@login_required
def my_events(request):
    events = request.user.events.filter(delete_date__isnull=True).order_by('event_date')
    return render(request, 'my_events.html', {'events': events})


@login_required
@user_passes_test(is_librarian)
def event_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        filial_id = request.POST.get('filial')
        max_participants = request.POST.get('max_participants', 0)

        if not title or not description or not event_date or not filial_id:
            messages.error(request, "Заполните обязательные поля.")
        else:
            Event.objects.create(
                title=title,
                description=description,
                event_date=event_date,
                filial_id=filial_id,
                max_participants=int(max_participants) if max_participants else 0
            )
            messages.success(request, "Мероприятие добавлено.")
            return redirect('event_list')

    filials = Filial.objects.filter(delete_date__isnull=True)
    return render(request, 'event_form.html', {'filials': filials, 'title': 'Добавление мероприятия'})


@login_required
@user_passes_test(is_librarian)
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.event_date = request.POST.get('event_date')
        event.filial_id = request.POST.get('filial')
        event.max_participants = int(request.POST.get('max_participants', 0))
        event.save()
        messages.success(request, "Мероприятие обновлено.")
        return redirect('event_list')

    filials = Filial.objects.filter(delete_date__isnull=True)
    return render(request, 'event_form.html', {
        'event': event,
        'filials': filials,
        'title': 'Редактирование мероприятия',
        'event_id': event.pk
    })


@login_required
@user_passes_test(is_librarian)
def event_soft_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.soft_delete()
    messages.success(request, f'Мероприятие "{event.title}" удалено.')
    return redirect('event_list')


@login_required
def profile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        if phone:
            profile.phone = phone
        if address:
            profile.address = address
        profile.save()
        messages.success(request, "Профиль обновлён.")
        return redirect('profile')
    return render(request, 'profile.html', {'profile': profile})


def statistics(request):
    from datetime import timedelta
    now = timezone.now()
    start_date = now - timedelta(days=180)
    requests_data = BookRequest.objects.filter(request_date__gte=start_date)

    months = []
    counts = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        count = requests_data.filter(request_date__range=(month_start, month_end)).count()
        months.append(month_start.strftime('%b %Y'))
        counts.append(count)

    plt.figure(figsize=(10, 5))
    plt.bar(months, counts, color='#CE5656')
    plt.title('Количество запросов книг за последние 6 месяцев', fontsize=14, color='#27408B')
    plt.xlabel('Месяц', fontsize=12)
    plt.ylabel('Количество запросов', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return render(request, 'statistics.html', {'graph': image_base64})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_deleted_books(request):
    deleted_books = Book.objects.filter(delete_date__isnull=False).order_by('-delete_date')
    return render(request, 'admin_deleted_list.html', {'deleted_books': deleted_books})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_restore(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.restore()
    messages.success(request, f'Книга "{book.title}" восстановлена.')
    return redirect('admin_deleted_books')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_permanent_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    title = book.title
    if book.image and os.path.isfile(book.image.path):
        os.remove(book.image.path)
    book.delete()
    messages.success(request, f'Книга "{title}" полностью удалена.')
    return redirect('admin_deleted_books')