from django.contrib import admin
from .models import Genre, Book, BookRequest, UserProfile, Filial, Event

admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(BookRequest)
admin.site.register(UserProfile)
admin.site.register(Filial)
admin.site.register(Event)