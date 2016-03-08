#from django import template
from django.http import Http404
from django.shortcuts import render
from django.template.defaulttags import register
from .models import Book

#register = template.Library()


# Create your views here.

@register.simple_tag
def get_item(dictionary, key1, key2):
    return dictionary.get(key1).get(key2)


def book(request, book_name):
    book_obj = Book.objects.filter(name__iexact=book_name).prefetch_related('accounts').first()
    if not book_obj:
        raise Http404("{} not found".format(book_name))

    purchases = {}
    for acc in book_obj.accounts.all():
        p_dict = {product.pk: 0 for product in book_obj.products.all()}
        spent = 0
        for pur in acc.purchases.all():
            spent = spent + pur.total_price
            for item in pur.items.all():
                p_item = p_dict[item.product_id]
                p_dict[item.product_id] = p_item + item.amount

        p_dict['spent'] = spent
        purchases[acc.pk] = p_dict
        print("{}'s purchases: {}".format(acc.user.username, p_dict))

    context = {'book': book_obj, 'purchases': purchases}
    return render(request, 'book.html', context)
