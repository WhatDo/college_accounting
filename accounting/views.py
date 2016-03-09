from datetime import datetime, timedelta

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils import dateparse
from .models import Book


# Create your views here.

@register.simple_tag
def get_item(dictionary, key1, key2):
    return dictionary.get(key1).get(key2)


@register.filter
def neg(number):
    return -number


def book(request, book_name):
    book_obj = Book.objects.filter(name__iexact=book_name).prefetch_related('accounts').first()

    low_date = request.GET.get('start')
    low_date = dateparse.parse_date(low_date) if low_date else None
    print('start date {}'.format(low_date))
    high_date = request.GET.get('end', 'not_a_date')
    high_date = dateparse.parse_date(high_date)
    if high_date:
        high_date = datetime(high_date.year, high_date.month, high_date.day) \
                    + timedelta(days=1, microseconds=-1)
    print('end date {}'.format(high_date))
    if not book_obj:
        raise Http404("{} not found".format(book_name))

    purchases = {}
    for acc in book_obj.accounts.all():
        p_dict = {product.pk: 0 for product in book_obj.products.all()}
        spent = 0
        psq = acc.purchases.all()
        if low_date:
            psq = psq.filter(date__gte=low_date)
        if high_date:
            psq = psq.filter(date__lte=high_date)

        for pur in psq:
            spent = spent + pur.total_price
            for item in pur.items.all():
                p_item = p_dict[item.product_id]
                p_dict[item.product_id] = p_item + item.amount

        dsq = acc.deposits.all()

        p_dict['deposited'] = dsq.aggregate(paid=Coalesce(Sum('amount'), 0))['paid']
        p_dict['spent'] = spent
        purchases[acc.pk] = p_dict

    context = {'book': book_obj, 'purchases': purchases}
    return render(request, 'book.html', context)
