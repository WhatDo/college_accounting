from django.shortcuts import render, get_object_or_404
from .models import Book


# Create your views here.

def book(request, book_name):
    book_obj = get_object_or_404(Book, name=book_name)
    context = {'book': book_obj}
    return render(request, 'book.html', context)
