from django.conf.urls import url
from .views import book

urlpatterns = [
        url(r'(?P<book_name>[a-zA-Z]+)/$', book, name='book_detail')
]