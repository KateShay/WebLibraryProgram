from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from libsayan import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная
    path('', views.index, name='index'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Книги
    path('books/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/request/', views.request_book, name='request_book'),
    path('book/create/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('book/<int:pk>/soft-delete/', views.book_soft_delete, name='book_soft_delete'),
    
    # Запросы
    path('my-requests/', views.my_requests, name='my_requests'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('return/<int:request_id>/', views.return_book, name='return_book'),
    
    # Мероприятия
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', views.register_for_event, name='register_event'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:pk>/soft-delete/', views.event_soft_delete, name='event_soft_delete'),
    path('my-events/', views.my_events, name='my_events'),
    
    # Профиль и статистика
    path('profile/', views.profile, name='profile'),
    path('statistics/', views.statistics, name='statistics'),
    
    # Админ корзина
    path('admin/deleted/', views.admin_deleted_books, name='admin_deleted_books'),
    path('admin/restore/<int:pk>/', views.book_restore, name='book_restore'),
    path('admin/permanent-delete/<int:pk>/', views.book_permanent_delete, name='book_permanent_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)